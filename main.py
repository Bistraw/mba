from flask import Flask, jsonify, request, send_file
import database
from domain import Color, Source, SourceKind, SourceFrame, SourceService
import render
import ingester
import io
from PIL import Image, ImageDraw

database.update_schema()

app = Flask(__name__)

@app.route('/source/<int:source_id>/render', methods=['GET'])
def get_source_render(source_id):
    
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


if __name__ == "__main__":
    app.run()