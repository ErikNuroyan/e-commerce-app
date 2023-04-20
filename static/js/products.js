
function App() {
  const [products, setProducts] = React.useState([]);
  const [cardProducts, setCardProducts] = React.useState(new Array());
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    // Get the products
    fetch('http://127.0.0.1:5000/products')
    .then(response => response.json())
    .then(products => {
      setProducts(products);
    })
    .catch(error => {
      setError(error);
    });

    //Get card information if logged in
    const token = localStorage.getItem("token");
    if (token !== null) {
      const requestOptions = {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
      };
      
      fetch('http://127.0.0.1:5000/user/card_products', requestOptions)
        .then(response => response.json())
        .then(response => {
          if (response.status != 200) {
            throw new Error('Error getting card info');
          }
          setCardProducts(response.card_products)
        })
        .catch(error => {
          alert(error);
        });
    }

  }, []);

  const handlePurchase = () => {
    if (localStorage.getItem("token") === null) {
      alert("Please Log in");
      return;
    }

    // Make a POST request to the server to purchase the product
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem("token")},
      body: JSON.stringify({ item_ids: cardProducts})
    };
    
    fetch('http://127.0.0.1:5000/products/purchase', requestOptions)
      .then(response => response.json())
      .then(response => {
        if (response.purchase_status != 200) {
          throw new Error('Error purchasing product');
        }
        alert('Products purchased successfully!');
      })
      .catch(error => {
        alert(error);
      });
  };

  const addToCard = productId => {
    if (localStorage.getItem("token") === null) {
      alert("Please Log in");
      return;
    }

    const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem("token")},
    body: JSON.stringify({ item_id: productId})
    };
    
    fetch('http://127.0.0.1:5000/user/add_to_card', requestOptions)
      .then(response => response.json())
      .then(response => {
        if (response.status != 200) {
          throw new Error('Error adding the product');
        }
        setCardProducts([productId, ...cardProducts]);
        alert('Product added to card successfully!');
      })
      .catch(error => {
        alert(error);
      });
  };

  const removeFromCard = productId => {
    if (localStorage.getItem("token") === null) {
      alert("You're not logged in");
      return;
    }

    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem("token")},
      body: JSON.stringify({ item_id: productId})
    };
    
    fetch('http://127.0.0.1:5000/user/remove_from_card', requestOptions)
      .then(response => response.json())
      .then(response => {
        if (response.status != 200) {
          throw new Error('Error removing the product from the card');
        }
        var array = [...cardProducts];
        var index = array.indexOf(productId);
        if (index !== -1) {
          array.splice(index, 1);
          setCardProducts(array);
        }
        alert('Product removed from the card successfully!');
      })
      .catch(error => {
        alert(error);
      });
  };

  return (
          <>
          {products.map(product => (
            <div className = "col" key = {"col_id" + product.id}>
              <img key = {"img_id" + product.id} src = "static/images/img.png" />
              <h2 key = {"name_id" + product.id}>{product.name}</h2>
              <h3 key = {"price_id" + product.id}>{product.price}$</h3>
              {cardProducts.includes(product.id) ?
               (
                <>
                <b> Added to Card</b>
                <button key = {"remove_from_card_button_id" + product.id} onClick={() => removeFromCard(product.id)}>
                Remove From Card
                </button>
                </>
               ) :
               <button key = {"add_to_card_button_id" + product.id} onClick={() => addToCard(product.id)}>
                Add To Card
               </button>}
            </div>
          ))}
          <button key = {"purchase_button_id"} onClick={handlePurchase}>
            Purchase
          </button>
          </>
        );
}


const domContainer = document.querySelector('#products');
const root = ReactDOM.createRoot(domContainer);
root.render(<App/>);

