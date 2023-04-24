from dotenv import load_dotenv
from flask_mysqldb import MySQL
from flask import Flask
import os
import csv

from flask_cors import CORS

from flask import jsonify, request

app = Flask(__name__)
CORS(app)

load_dotenv()

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE')

mysql = MySQL(app)


@app.route('/')
def index():
    return "Welcome to the API!"


@app.route('/csv-to-db')
def scraper():
    cursor = mysql.connection.cursor()
    # create table
    cursor.execute("DROP TABLE products")

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS products (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), price VARCHAR(255), image VARCHAR(255), link VARCHAR(255))")

    # clear table
    cursor.execute("TRUNCATE TABLE products")

    # insert data into table
    with open('kimironko.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row.
        for row in reader:
            cursor.execute(
                'INSERT INTO products (name, price, image, link) VALUES (%s, %s, %s, %s)', row)

    with open('beiMart.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row.
        for row in reader:
            cursor.execute(
                'INSERT INTO products (name, price, image, link) VALUES (%s, %s, %s, %s)', row)

    with open('olado.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row.
        for row in reader:
            cursor.execute(
                'INSERT INTO products (name, price, image, link) VALUES (%s, %s, %s, %s)', [row[0], row[1].replace(",", ""), row[2], row[3]])

    # commit changes
    mysql.connection.commit()

    # close connection
    cursor.close()

    return "Tables created and products added"


# get all products and return json
@app.route('/products')
def products():
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM products")
    if result > 0:
        products = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
        return jsonify(products)
    else:
        return "No products found"


# get similar products given a product name
@app.route('/products/get-similar', methods=['POST'])
def get_similar():
    try:
        # get `name` from request body
        name = request.json['name']
    except KeyError:
        return "Name not found in request body"

    # get all products
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM products")
    if result > 0:
        products = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
        # similar products logic: 1) same name 2) some words in name are in common 3) full names do not have to be the same
        similar_products = []
        for product in products:
            productObj = {
                "id": product[0],
                "name": product[1],
                # 70, 000 to 70000
                "price": int(product[2].replace(',', '')),
                "image": product[3],
                "link": product[4]
            }
            to_remove_from_search_stop_words = ["for", "and", "of", "the", "in", "a", "an", "with", "to", "from", "on", "at", "by", "into", "over", "under", "off", "up", "down", "out", "around", "about", "between", "across", "behind", "beyond", "during", "inside", "outside", "through", "toward", "towards", "up", "upon", "down", "down"]
            all_words_to_search = [x.lower() for x in name.split(" ")]
            all_words_to_search = [x for x in all_words_to_search if x not in to_remove_from_search_stop_words]
            for word in all_words_to_search:
                if word in [x.lower() for x in product[1].split(" ")]:
                    similar_products.append(productObj)

        sortedByPrice = sorted(
            similar_products, key=lambda k: int(k['price']))
        
        indices_to_remove = []

        # check suggested similar products for products with similar names, if similar names, we check link, if link is the same, we remove it
        print(len(sortedByPrice))
        for i in range(len(sortedByPrice)):
            for j in range(len(sortedByPrice)):
                if sortedByPrice[i]['name'] == sortedByPrice[j]['name'] and sortedByPrice[i]['link'] == sortedByPrice[j]['link'] and i != j:
                    indices_to_remove.append(j)
        
        indices_to_remove = list(set(indices_to_remove))
        print(indices_to_remove)

        # reverse sort indices to remove
        indices_to_remove.sort(reverse=True)

        for index in indices_to_remove:
            print(sortedByPrice)
            del sortedByPrice[index]
        

        return jsonify(sortedByPrice)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("PORT", default=5000), debug=True)
