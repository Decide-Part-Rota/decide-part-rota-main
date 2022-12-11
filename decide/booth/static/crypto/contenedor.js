'use strict';

const create = React.createElement;

class Contenedor extends React.Component {
  

  render() {


    return create(
      'header',{},
        create("div", {className: "flip-card"},
          create("div", {className: "flip-card-inner"},
            create("div", {className: "flip-card-front"},
              create('h1',{className:'Logo'},"Let's vote!")),

            create("div", {className: "flip-card-back"},
              create('h3',{className:'Logo'},"Not sure on what to vote?")))),
    );
  }
}

const domContainer = document.querySelector('#contenedor');
const root = ReactDOM.createRoot(domContainer);
root.render(create(Contenedor));