from flask import Flask, jsonify, request, send_file, render_template
import database
from domain import Color, Source, SourceKind, SourceFrame, SourceService
import render
import ingester
import os
import io
from PIL import Image, ImageDraw

database.update_schema()

app = Flask(__name__)

@app.route('/api/source/<int:source_id>/render', methods=['GET'])
def api_get_source_render(source_id):
    
    height = request.args.get('height', default=900, type=int)
    width = request.args.get('width', default=1000, type=int)
    strip_width = request.args.get('strip_width', default=5, type=int)
    max_strips = request.args.get('max_strips', default=1000, type=int)

    conn = database.create_connection()
    
    frames = SourceService.get_source_frames(conn, source_id)

    data = []

    for f in frames:
        data.append(f.color)

    img : Image = render.render_force_max_lines_force_size(data, height, strip_width, max_strips, width)
    
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

    return render_template('source_list.html', sources=sources)

@app.route('/source/<int:source_id>/render', methods=['GET'])
def get_source_render(source_id):
    height = request.args.get('height', default=900, type=int)
    width = request.args.get('width', default=1000, type=int)
    strip_width = request.args.get('strip_width', default=5, type=int)
    max_strips = request.args.get('max_strips', default=1000, type=int)

    conn = database.create_connection()
    source = SourceService.get_source_by_id(conn, source_id)
    frames = SourceService.get_source_frames(conn, source_id)

    return render_template('source_render.html', source=source, frames=frames, height=height, width=width, strip_width=strip_width, max_strips=max_strips)

@app.route('/static/<path:filename>')
def static_css(filename):
    return send_file(os.path.join('static', 'css', filename))

if __name__ == "__main__":
    app.run()