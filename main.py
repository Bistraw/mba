from flask import Flask, jsonify, request, send_file, send_from_directory, render_template
import database
from domain import Color, ColorMode, RenderKind, Source, SourceKind, SourceFrame, SourceService
import render
import ingester
import os
import io
from PIL import Image, ImageDraw

database.update_schema()

app = Flask(__name__)

def is_it_true(value):
    print(f"is_it_true, value: {value}")
  
    return value.lower() == 'true'

@app.route('/api/source/<int:source_id>/render', methods=['GET'])
def api_get_source_render(source_id):
    
    height = request.args.get('height', default=900, type=int)
    width = request.args.get('width', default=1000, type=int)
    strip_width = request.args.get('strip_width', default=5, type=int)
    max_strips = request.args.get('max_strips', default=1000, type=int)
    kind = request.args.get('kind', default=RenderKind.LINE, type=int)
    radius = request.args.get('radius', default=400, type=int)
    radius_inner = request.args.get('radius_inner', default=20, type=int)
    turns = request.args.get('turns', default=6, type=int)
    color_mode = request.args.get('color_mode', default=ColorMode.AVERAGE, type=int)

    f_ = request.args.get('f', default=False, type=is_it_true)
    f_bg_r = request.args.get("f_bg_r", default=250, type=int)
    f_bg_g = request.args.get("f_bg_g", default=250, type=int)
    f_bg_b = request.args.get("f_bg_b", default=250, type=int)
    f_fg_r = request.args.get("f_fg_r", default=0, type=int)
    f_fg_g = request.args.get("f_fg_g", default=0, type=int)
    f_fg_b = request.args.get("f_fg_b", default=0, type=int)
    f_h_h = request.args.get("f_h_h", default=20, type=int)
    
    #f_t_l = request.args.get("f_t_l", default="frame title", type=str)

    print(f"request processing... f_: {f_}")

    conn = database.create_connection()

    source = SourceService.get_source_by_id(conn, source_id)

    if not ColorMode.is_valid(color_mode):
        return jsonify(error=f"unknown color_mode: {color_mode}"), 400

    if not RenderKind.is_valid(kind):
        return jsonify(error=f"unknown kind: {kind}"), 400

    data = SourceService.get_source_colors(conn, source_id, color_mode)

    if data is None:
        return jsonify(error="this source has no data for this color mode yet, run feeder.py to backfill it"), 409

    if kind == RenderKind.LINE:
        img : Image = render.render_force_max_lines_force_size(data, height, strip_width, max_strips, width)
    elif kind == RenderKind.CIRCLE:
        img : Image = render.render_circle(data, radius, radius_inner, max_strips, width, height)
    elif kind == RenderKind.ROWS:
        img : Image = render.render_rows(data, max_strips, width, height)
    elif kind == RenderKind.RINGS:
        img : Image = render.render_rings(data, radius, radius_inner, max_strips, width, height)
    elif kind == RenderKind.SPIRAL:
        img : Image = render.render_spiral(data, radius, radius_inner, max_strips, width, height, turns)
    elif kind == RenderKind.MOSAIC:
        img : Image = render.render_mosaic(data, max_strips, width, height)
    else:
        img : Image = render.render_wave(data, max_strips, width, height)

    if f_ == True:
        img : Image = render.render_frame(f"{source.metadata_name} ({source.metadata_year})", "", img, Color(f_bg_r, f_bg_g, f_bg_b), Color(f_fg_r, f_fg_g, f_fg_b), f_h_h, width, height)
    
    img_io = io.BytesIO()
    
    img.save(img_io, 'PNG')
    
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/api/source/list', methods=['GET'])
def api_get_source_list():
    conn = database.create_connection()
    sources = SourceService.get_sources(conn)
    return jsonify([s.__dict__ for s in sources])

@app.route('/source/list', methods=['GET'])
def get_source_list():
    conn = database.create_connection()
    sources = SourceService.get_sources(conn)

    return render_template('source_list.html', sources=sources, color_modes=ColorMode.ALL)

@app.route('/source/<int:source_id>/render', methods=['GET'])
def get_source_render(source_id):
    height = request.args.get('height', default=900, type=int)
    width = request.args.get('width', default=1000, type=int)
    strip_width = request.args.get('strip_width', default=5, type=int)
    max_strips = request.args.get('max_strips', default=1000, type=int)
    kind = request.args.get('kind', default=RenderKind.LINE, type=int)
    radius = request.args.get('radius', default=400, type=int)
    radius_inner = request.args.get('radius_inner', default=20, type=int)
    turns = request.args.get('turns', default=6, type=int)
    color_mode = request.args.get('color_mode', default=ColorMode.AVERAGE, type=int)
    f_ = request.args.get('f', default=False, type=is_it_true)

    conn = database.create_connection()
    source = SourceService.get_source_by_id(conn, source_id)

    return render_template('source_render.html', source=source, height=height, width=width, strip_width=strip_width, max_strips=max_strips, kind=kind, radius=radius, radius_inner=radius_inner, turns=turns, color_mode=color_mode, color_modes=ColorMode.ALL, render_kinds=RenderKind.ALL, radial_kinds=RenderKind.RADIAL, f=f_)

@app.route('/assets/fonts/<path:filename>')
def asset_fonts(filename):
    # the ui uses the same fonts as the framed renders
    return send_from_directory(os.path.join('assets', 'fonts'), filename)

@app.route('/static/<path:filename>')
def static_css(filename):
    return send_file(os.path.join('static', 'css', filename))

if __name__ == "__main__":
    app.run()