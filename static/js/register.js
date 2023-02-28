class RegisterForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isOpen : false, email : "", name : "", address : "", phoneNumber : "", password1 : "", password2 : ""};

  }

  handleSubmit = (e) => {
      e.preventDefault();
      if (this.state.email === "") {
          alert("Please enter email");
          return;
      }
      
      if (this.state.name === "") {
          alert("Please enter name");
          return;
      }
      
      if (this.state.address === "") {
          alert("Please enter address");
          return;
      }
      
      if (this.state.phoneNumber === "") {
          alert("Please enter phone number");
          return;
      }
      
      if (this.state.password1 === "") {
          alert("Please enter password");
          return;
      }
      
      if (this.state.password2 === "") {
          alert("Please confirm the password");
          return;
      }
      
      if (this.state.password1 !== this.state.password2) {
          alert("The passwords don't match!");
          return;
      }
      
      fetch("http://127.0.0.1:8787/register", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email : this.state.email,
          name : this.state.name,
          address : this.state.address,
          phone_number : this.state.phoneNumber,
          password : this.state.password1
        }),
      }).then(response => response.json())
        .then(response => {
          if (response.register_status != 200) {
            throw new Error(response.message);
          }
          alert('User registered successfully!');
        }).catch(error => {
          alert(error);
        });
  };
    
  render() {
    if (this.state.isOpen) {
        return (
            <form action="/register" method="post" onSubmit={this.handleSubmit}>
              <label htmlFor="email">E-Mail: </label>
              <br/>
              <input type="email" id="email" name="email" onChange={(e) => this.setState({email : e.target.value})}/>
              <br/>

              <label htmlFor="name">Name: </label>
              <br/>
              <input type="text" id="name" name="name" onChange={(e) => this.setState({name : e.target.value})}/>
              <br/>

              <label htmlFor="address">Address: </label>
              <br/>
              <input type="text" id="address" name="address" onChange={(e) => this.setState({address : e.target.value})}/>
              <br/>

              <label htmlFor="phone_number">Phone Number: </label>
              <br/>
              <input type="text" id="phone_number" name="phone_number" onChange={(e) => this.setState({phoneNumber : e.target.value})}/>
              <br/>

              <label htmlFor="password1">Password: </label>
              <br/>
              <input type="password" id="password1" name="password1" onChange={(e) => this.setState({password1 : e.target.value})}/>
              <br/>

              <label htmlFor="password2">Confirm Password: </label>
              <br/>
              <input type="password" id="password2" name="password2" onChange={(e) => this.setState({password2 : e.target.value})}/>
              <br/>

              <input type="submit" value="Register"/>
              <button type="button" onClick={() =>
                    this.setState({isOpen : false})
                }>Cancel</button>
              <br/>
            </form>
        );
    }
    else {
        return (
            <button key = {"register"} onClick={() => this.setState({isOpen : true})}>
              Register
            </button>
        );
    }
  }
}

const root = ReactDOM.createRoot(document.getElementById('register'));
root.render(<RegisterForm />);

