'use strict';

const create = React.createElement;
const datos = document.getElementById("hide").value;
const dicc = JSON.parse(voting);

//const view = [];
const keys = Object.keys(dicc);

const id = keys[0];
const lista = dicc[0];
const nombre = lista[1];
const desc = lista[2];



  //view.push(aux)



class Contenedor extends React.Component {

  render() {


    return create("body", {}, 
      create("fiv",{key: "id", className: "flip-card"},
      create("td",{key: "name", className: "flip-card-inner"},
      create("td",{key: "desc", className: "flip-card-front"},nombre),
      create("div", {className: "flip-card-back"},
      create('h3',{className:'Logo'},desc)))),


);
    
  }
}



const domContainer = document.querySelector('#caja');
const root = ReactDOM.createRoot(domContainer);
root.render(create(Contenedor));