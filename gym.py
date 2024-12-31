import os
from flask import Flask, render_template, json, request, redirect, flash, url_for, session
from werkzeug.utils import secure_filename
import random 

app = Flask(__name__)




@app.route('/')
def home(): 
    return render_template('index.html')


@app.route('/products')
def products():
    return render_template('productcat.html')

with open('shoes.json', 'r') as s:
    shoes_data=json.load(s)

with open('men.json', 'r') as m:
    mens_data=json.load(m)

with open('women.json', 'r') as w:
    womens_data = json.load(w)

with open('trousers.json', 'r') as t:
    trousers_data = json.load(t)

with open('bags.json', 'r') as f:
    bags_data = json.load(f)

@app.route('/shoes', methods=['GET'])
def shoes():
    sort_by = request.args.get('sort_by')
    shoes = shoes_data['shoes']

    # Sort the bags based on the query parameter
    if sort_by == 'low_to_high':
        shoes = sorted(shoes, key=lambda x: x['price'])
    elif sort_by == 'high_to_low':
        shoes = sorted(shoes, key=lambda x: x['price'], reverse=True)

    return render_template('shoes.html', shoes=shoes)

@app.route('/trousers', methods=['GET'])
def trousers():
    sort_by = request.args.get('sort_by')
    trousers = trousers_data['trousers']

    # Sort the trousers based on the query parameter
    if sort_by == 'low_to_high':
        trousers = sorted(trousers, key=lambda x: x['price'])
    elif sort_by == 'high_to_low':
        trousers = sorted(trousers, key=lambda x: x['price'], reverse=True)

    return render_template('trousers.html', trousers=trousers)

@app.route('/men', methods=['GET'])
def mens():
    sort_by = request.args.get('sort_by')
    mens = mens_data['men']

    if sort_by == 'low_to_high':
        mens = sorted(mens, key=lambda x: x['price'])
    elif sort_by == 'high_to_low':
        mens = sorted(mens, key=lambda x: x['price'], reverse=True)

    return render_template('men.html', mens=mens)

@app.route('/women', methods=['GET'])
def womens():
    sort_by = request.args.get('sort_by')
    womens = womens_data['women']

    if sort_by == 'low_to_high':
        womens = sorted(mens, key=lambda x: x['price'])
    elif sort_by == 'high_to_low':
        womens = sorted(mens, key=lambda x: x['price'], reverse=True)

    return render_template('women.html', womens=womens)

@app.route('/dufflebags', methods=['GET'])
def dufflebags():
    sort_by = request.args.get('sort_by')
    bags = bags_data['bags']

    if sort_by == 'low_to_high':
        bags = sorted(bags, key=lambda x: x['price'])
    elif sort_by == 'high_to_low':
        bags = sorted(bags, key=lambda x: x['price'], reverse=True)

    return render_template('dufflebags.html', bags=bags)

@app.route('/productdetails/<path:productname>', methods=['GET'])
def product_detail(productname):
    productname = productname.lower()

    # Try to find the product in bags_data
    product = next((bag for bag in bags_data['bags'] if bag['name'].lower() == productname), None)
    
    if not product:
        # If not found, try to find the product in shoes_data
        product = next((shoe for shoe in shoes_data['shoes'] if shoe['name'].lower() == productname), None)

    if not product:
        # If not found, try to find the product in trousers_data
        product = next((trouser for trouser in trousers_data['trousers'] if trouser['name'].lower() == productname), None)

    if not product:
        # If not found, try to find the product in mens_data
        product = next((men for men in mens_data['men'] if men['name'].lower() == productname), None)

    if not product:
        # If not found, try to find the product in womens_data
        product = next((women for women in womens_data['women'] if women['name'].lower() == productname), None)

    if product:
        # Determine the category of the current product
        if product in bags_data['bags']:
            category_products = bags_data['bags']
        elif product in shoes_data['shoes']:
            category_products = shoes_data['shoes']
        elif product in trousers_data['trousers']:
            category_products = trousers_data['trousers']
        elif product in mens_data['men']:
            category_products = mens_data['men']
        else:  # The product must be from womens_data
            category_products = womens_data['women']

        # Get 4 random products from the appropriate category
        random_products = random.sample([p for p in category_products if p['name'] != product['name']], k=min(4, len(category_products) - 1))

        return render_template('productdetail.html', product=product, random_products=random_products)
    else:
        return "Product not found", 404


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

app.secret_key = '***********'  

VALID_USERNAME = '*********'
VALID_PASSWORD = '**********'



@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        session['logged_in'] = True  # Set session variable to indicate login
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('admin'))


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):  # Check if user is logged in
        flash('You need to log in first.')
        return redirect(url_for('admin'))
    
    # Render the dashboard with all product categories
    return render_template('dashboard.html', 
                           shoes=shoes_data['shoes'],
                           mens=mens_data['men'],
                           womens=womens_data['women'],
                           trousers=trousers_data['trousers'],
                           bags=bags_data['bags'])

# Allowed image file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'logged_in' not in session or not session['logged_in']:
        flash('You need to log in first.')
        return redirect(url_for('admin'))

    category = request.form['category']
    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    images = request.files.getlist('images')
    url = request.form['url']

    if len(images) != 4:
        flash("Please upload exactly 4 images.")
        return redirect(url_for('dashboard'))

    # Find the correct data and last product number
    if category == 'shoes':
        products_data = shoes_data['shoes']
        image_prefix = 'shoe'
        json_file = 'shoes.json'
    elif category == 'men':
        products_data = mens_data['men']
        image_prefix = 'men'
        json_file = 'men.json'
    elif category == 'women':
        products_data = womens_data['women']
        image_prefix = 'women'
        json_file = 'women.json'
    elif category == 'trousers':
        products_data = trousers_data['trousers']
        image_prefix = 'trouser'
        json_file = 'trousers.json'
    elif category == 'bags':
        products_data = bags_data['bags']
        image_prefix = 'bag'
        json_file = 'bags.json'

    # Determine the next product number
    last_product = products_data[-1]
    last_image = last_product['images'][0]
    last_number = int(last_image.split(image_prefix)[-1].split('img')[0])

    # Increment product number
    new_product_number = last_number + 1

    # Save images
    image_paths = []
    for i, image in enumerate(images, start=1):
        if allowed_file(image.filename):
            filename = secure_filename(f"{image_prefix}{new_product_number}img{i}.jpg")
            image.save(os.path.join('static/images', category, filename))
            image_paths.append(f"{category}/{filename}")
        else:
            flash('Invalid image format. Only png, jpg, jpeg, gif are allowed.')
            return redirect(url_for('dashboard'))

    # Create new product
    new_product = {
        "name": name,
        "price": int(price),
        "description": description,
        "link": url,  
        "images": image_paths
    }

    # Add to JSON
    products_data.append(new_product)
    with open(json_file, 'w') as f:
        json.dump({category: products_data}, f, indent=4)

    flash('Product added successfully!')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Log out by clearing the session
    flash('You have been logged out.')
    return redirect(url_for('admin'))


import os
import json
from flask import flash, redirect, url_for

@app.route('/delete_product/<category>/<productname>', methods=['POST'])
def delete_product(category, productname):
    productname = productname.lower()
    
    # Define the path to the images folder
    images_folder = os.path.join('static', 'images')

    # Load the corresponding data based on the category
    if category == 'shoes':
        products_data = shoes_data['shoes']
        json_file = 'shoes.json'
    elif category == 'men':
        products_data = mens_data['men']
        json_file = 'men.json'
    elif category == 'women':
        products_data = womens_data['women']
        json_file = 'women.json'
    elif category == 'trousers':
        products_data = trousers_data['trousers']
        json_file = 'trousers.json'
    elif category == 'bags':
        products_data = bags_data['bags']
        json_file = 'bags.json'
    else:
        flash('Invalid category')
        return redirect(url_for('dashboard'))

    # Find the product and remove it
    updated_products_data = []
    for product in products_data:
        if product['name'].lower() == productname:
            # Delete all associated images
            for image_name in product.get('images', []):  # Use .get() to avoid KeyError
                image_path = os.path.join(images_folder, image_name)
                if os.path.exists(image_path):
                    os.remove(image_path)
        else:
            updated_products_data.append(product)

    # Save the updated data back to the JSON file
    with open(json_file, 'w') as f:
        json.dump({category: updated_products_data}, f, indent=4)

    flash('Product deleted successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
