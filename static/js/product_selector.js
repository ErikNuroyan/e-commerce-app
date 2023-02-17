class ProductSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isOpen: false, uniqueProducts : [], selectedProductId : 1};
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  fetchUniqueItems = () => {
    fetch('http://127.0.0.1:8787/unique_products')
        .then(response => response.json())
        .then(result => {
            this.setState({uniqueProducts: result})
        })
        .catch(e => {
            console.log(e);
            this.setState({...this.state});
        });
  };

  handleSubmit = (e) => {
    e.preventDefault();
    if (typeof this.props.replaceItemId === 'undefined') {
        this.props.submitCallback(this.state.selectedProductId);
    }
    else {
        this.props.submitCallback(this.props.replaceItemId, this.state.selectedProductId);
    }
    
  };
    
  handleChange = (e) => {
      this.setState({selectedProductId : parseInt(e.target.value)});
  };
  
  render() {
    if (this.state.isOpen) {
        return (
            <>
                <form action={this.props.action} method="post" onSubmit={this.handleSubmit}>
                    <label htmlFor="unique_products">Choose the product:</label>
                    <br/>
                    <select name="unique_products" id="unique_products" onChange={this.handleChange}>
                        {
                            this.state.uniqueProducts.map(product => (
                            <option key={product.id} value={product.id}>{product.name}</option>))
                        }
                    </select>
                    <br/>
                    <input type="submit" value={this.props.buttonName}/>
                    <button type="button" onClick={() =>
                        this.setState({isOpen : false})
                    }>Cancel</button>
                    <br/>
                </form>
            </>
        );
    }
    else {
        return (
                <button key = {"button"} onClick={() => {
                    this.setState({isOpen : true});
                    this.fetchUniqueItems();
                }}>
                    {this.props.buttonName}
                </button>
        );
    }
  }
}

