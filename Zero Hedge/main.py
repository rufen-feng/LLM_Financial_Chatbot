# from Flask import Flask, render_template, request, jsonify
from Zero_Scraper import main, stop, observer

scraping = False
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('zero.html', terminal_output="", listing_data={})


@app.route('/search', methods=['POST'])
def search():
    global scraping
    if not scraping:
        scraping = True
        data = request.json
        query = data.get('product')
        main(query=query)
        scraping = False
        return jsonify({'message': 'Scraping successfully!'})
    else:
        return jsonify({'message': 'Already Scraping!'})


prev_data = None


@app.route('/data')
def get_file_data():
    global prev_data
    data = observer.data
    if data:
        if data != prev_data:
            prev_data = data
            return jsonify(data)
        else:
            return jsonify(None)
    else:
        return jsonify(None)



@app.route('/terminate-subprocess', methods=['POST'])
def terminate_subprocess():
    stop()
    return jsonify({'message': 'Subprocess terminated successfully!'})


if __name__ == '__main__':
    app.run()
