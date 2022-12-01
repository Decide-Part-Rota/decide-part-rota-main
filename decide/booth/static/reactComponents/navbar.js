'use strict';

const create = React.createElement;

class Navbar extends React.Component {
  
  render() {

    const styles = {
      marginTop: 0,
    };

    return create(
      'header',{},
      create('h1',{className:'Logo'},"Decide Booth"),
      create('nav', {className:'NavBar'},
        create("ul",{className: "nav_links"},
          create("li",{},
            create("a",{href: "#", className: "Link"}, "Publicas")),
          create("li",{},
            create("a",{href: "#", className: "Link"}, "Privadas")),
          create("li",{},
            create("a",{href: "#", className: "Link"}, "Ayuda")),
        ),
      ),
      create('a',{className:'cta', href: "#"}, 
        create('button',{}, "Log Off"),
      ),
    );
  }
    
}

const domContainer = document.querySelector('#navbar');
const root = ReactDOM.createRoot(domContainer);
root.render(create(Navbar));
