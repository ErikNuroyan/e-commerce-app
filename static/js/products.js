
function App() {
  const [products, setProducts] = React.useState([]);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    fetch('http://127.0.0.1:8787/store/products')
      .then(response => response.json())
      .then(products => {
        setProducts(products);
      })
      .catch(error => {
        setError(error);
      });
  }, []);

  const handlePurchase = productId => {
    // Make a POST request to the server to purchase the product
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: productId})
    };
      
    fetch('http://127.0.0.1:8787/store/purchase', requestOptions)
      .then(response => response.json())
      .then(response => {
        if (response.purchase_status != 200) {
          throw new Error('Error purchasing product');
        }
        alert('Product purchased successfully!');
      })
      .catch(error => {
        console.error(error);
        alert('Error purchasing product');
      });
  };

  const handleDelete = productId => {
    // Make a POST request to the server to delete the product
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: productId})
    };
      
    fetch('http://127.0.0.1:8787/store/delete', requestOptions)
      .then(response => response.json())
      .then(response => {
        if (response.delete_status != 200) {
          throw new Error('Error deleting product');
        }
        alert('Product deleted successfully!');
      })
      .catch(error => {
        console.error(error);
        alert('Error deleting product');
      });
  };

  const addToStore = (productId) => {
    fetch("http://127.0.0.1:8787/store/add", {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selected_item_id : productId
      })
    }).then(response => response.json())
      .then(response => {
       if (response.add_to_store_status != 200) {
         throw new Error('Error adding the product to the store');
       }
       alert('Product added to the store successfully!');
     })
     .catch(error => {
       console.error(error);
       alert('Error adding the product to the store');
     });
  };

  const updateStoreItem = (replaceItemId, selectedItemId) => {
    fetch("http://127.0.0.1:8787/store/update", {
      method: "PUT",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        replace_item_id : replaceItemId,
        selected_item_id : selectedItemId
      })
    }).then(response => response.json())
      .then(response => {
       if (response.update_status != 200) {
         throw new Error('Error updating the product');
       }
       alert('Product updated successfully!');
     })
     .catch(error => {
       console.error(error);
       alert('Error updating the product');
     });
  };


  return (
          <>
          <ProductSelector submitCallback = {addToStore} buttonName = "Add to Store" action = "/store/add"/>
          {products.map(product => (
            <div className = "col" key = {"col_id" + product.id}>
              <img key = {"img_id" + product.id} src = "static/images/img.png" />
              <h2 key = {"name_id" + product.id}>{product.name}</h2>
              <h3 key = {"price_id" + product.id}>{product.price}$</h3>
              <button key = {"purchase_button_id" + product.id} onClick={() => handlePurchase(product.id)}>
                Purchase
              </button>
              <button key = {"delete_button_id" + product.id} onClick={() => handleDelete(product.id)}>
                Delete
              </button>
              <ProductSelector submitCallback = {updateStoreItem} buttonName = "Update" action = "/store/update" replaceItemId = {product.id}/>
            </div>
          ))}
          </>
        );
}


const domContainer = document.querySelector('#products');
const root = ReactDOM.createRoot(domContainer);
root.render(<App/>);

