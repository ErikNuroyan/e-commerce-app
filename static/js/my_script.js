
function App() {
  const [products, setProducts] = React.useState([]);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    fetch('http://127.0.0.1:8787/products')
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
      
    fetch('http://127.0.0.1:8787/purchase', requestOptions)
      .then(response => {
        if (!response.ok) {
          throw new Error('Error purchasing product');
        }
        alert('Product purchased successfully!');
      })
      .catch(error => {
        console.error(error);
        alert('Error purchasing product');
      });
  };

  return (
          <>
          {products.map(product => (
            <div className = "col" key = {"col_id" + product.id}>
              <img key = {"img_id" + product.id} src = "static/images/img.png" />
              <h2 key = {"name_id" + product.id}>{product.name}</h2>
              <h3 key = {"price_id" + product.id}>{product.price}$</h3>
              <button key = {"button_id" + product.id} onClick={() => handlePurchase(product.id)}>
                Purchase
              </button>
            </div>
          ))}
          </>
        );
}

const domContainer = document.querySelector('#products');
const root = ReactDOM.createRoot(domContainer);
root.render(<App clas/>);

