'use strict';

const create = React.createElement;

class Navbar extends React.Component {
  
  render() {
    return create(
      'header',{},
      create('h1',{className:'Logo'},"Decide Booth"),
      create('nav', {className:'NavBar'},
        create("ul",{className: "nav_links"},
          create("li",{},
            create("a",{href: "/booth/boothList", className: "Link"}, "Public")),
          create("li",{},
            create("a",{href: "/booth/boothListPrivate", className: "Link"}, "Private")),
          create("li",{},
            create("a",{href: "/booth/1/", className: "Link"}, "Ayuda")),
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
