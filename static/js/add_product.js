class AddProduct extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isOpen : false, name : "", description : "", price : -1, quantity : -1};

  }

  handleSubmit = (e) => {
      e.preventDefault();
      if (this.state.name == "") {
          alert("Please enter name");
          return;
      }
      
      if (this.state.description == "") {
          alert("Please enter description");
          return;
      }
      
      if (this.state.price == -1) {
          alert("Please enter price");
          return;
      }
      
      if (this.state.quantity == -1) {
          alert("Please enter quantity");
          return;
      }
      
     fetch("http://127.0.0.1:8787/products/add", {
       method: "POST",
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
         name : this.state.name,
         description : this.state.description,
         price : this.state.price,
         quantity: this.state.quantity
       }),
     }).then(response => response.json())
       .then(response => {
        if (response.add_status != 200) {
          throw new Error('Error adding the product');
        }
        alert('Product added successfully!');
      }).catch(error => {
        console.error(error);
        alert('Error adding the product');
      });
  };
    
  render() {
    if (this.state.isOpen) {
        return (
            <form action="/products/add" method="post" onSubmit={this.handleSubmit}>
              <label htmlFor="pname">Product Name:</label>
              <br/>
              <input type="text" id="pname" name="pname" onChange={(e) => this.setState({name : e.target.value})}/>
              <br/>
              <label htmlFor="description">Product Description:</label>
              <br/>
              <input type="text" id="description" name="description" onChange={(e) => this.setState({description : e.target.value})}/>
              <br/>
              <label htmlFor="price">Price in dollars:</label>
              <br/>
              <input type="number" id="price" name="price" min="1" onChange={(e) => this.setState({price : parseInt(e.target.value)})}/>
              <br/>
              <label htmlFor="quantity">Quantity:</label>
              <br/>
              <input type="number" id="quantity" name="quantity" min="1" onChange={(e) => this.setState({quantity : parseInt(e.target.value)})}/>
              <br/>

              <input type="submit" value="Add"/>
              <button type="button" onClick={() =>
                    this.setState({isOpen : false})
                }>Cancel</button>
              <br/>
            </form>
        );
    }
    else {
        return (
            <button key = {"add_product_button"} onClick={() => this.setState({isOpen : true})}>
              Add Product
            </button>
        );
    }
  }
}

const root = ReactDOM.createRoot(document.getElementById('add_product'));
root.render(<AddProduct />);
