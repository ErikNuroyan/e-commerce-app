class LoginForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isLoggedIn : localStorage.getItem("token") !== null, isOpen : false, email : "", password : ""};
  }

  handleLogIn = (e) => {
      e.preventDefault();
      if (this.state.email === "") {
          alert("Please enter email");
          return;
      }
      
      if (this.state.password === "") {
          alert("Please enter password");
          return;
      }

      if (this.state.isLoggedIn) {
        alert("You are already logged in");
        return;
      }
      
      fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email : this.state.email,
          password : this.state.password
        }),
      }).then(response => response.json())
        .then(response => {
          if (response.login_status != 200) {
            throw new Error(response.message);
          }
          localStorage.setItem("token", response.access_token);
          localStorage.setItem("user_name", response.user_name);
          this.setState({isLoggedIn : true});
          alert('Login Successful!');
        }).catch(error => {
          alert(error);
        });
  };

  handleLogOut = (e) => {
    e.preventDefault();

    if (!this.state.isLoggedIn) {
      alert("You are not logged in");
      return;
    }
    
    fetch("http://127.0.0.1:5000/logout", {
      method: "POST",
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem("token")}
    }).then(response => response.json())
      .then(response => {
        if (response.logout_status != 200) {
          throw new Error(response.message);
        }

        this.setState({isLoggedIn : false})
        localStorage.removeItem("token");
        localStorage.removeItem("user_name");
        alert('Successfully logged out');
      }).catch(error => {
        alert(error);
      });
};
    
  render() {
    if (this.state.isLoggedIn) {
      return (
        <>
          <b> Welcome, {localStorage.getItem("user_name")} </b>
          <button type="button" onClick={this.handleLogOut}> Log Out </button>
        </>
      );
    }
    else {
      if (this.state.isOpen) {
        return (
            <form action="/login" method="post" onSubmit={this.handleLogIn}>
              <label htmlFor="email">E-Mail: </label>
              <br/>
              <input type="email" id="email" name="email" onChange={(e) => this.setState({email : e.target.value})}/>
              <br/>

              <label htmlFor="password">Password: </label>
              <br/>
              <input type="password" id="password" name="password" onChange={(e) => this.setState({password : e.target.value})}/>
              <br/>

              <input type="submit" value="Log in"/>
              <button type="button" onClick={() =>
                    this.setState({isOpen : false})
                }>Cancel</button>
              <br/>
            </form>
        );
      }
      else {
          return (
              <button key = {"login"} onClick={() => this.setState({isOpen : true})}>
                Log in
              </button>
          );
      }
    }

  }
}

const root = ReactDOM.createRoot(document.getElementById('login'));
root.render(<LoginForm />);
