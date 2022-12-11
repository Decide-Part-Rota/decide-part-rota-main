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
            create("a",{href: "/booth/boothList", className: "Link"}, "Open Votings")),
          create("li",{},
            create("a",{href: "/booth/boothListPrivate", className: "Link"}, "My Votings")),
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
