'use strict';

const create = React.createElement;
const datos = document.getElementById("hide").value;
//const dicc = Array.map(voting);

const nombreBueno = voting.name
const id = voting.id
const desc = voting.desc

//const view = [];
//const keys = Object.keys(dicc);

//const id = keys[0];
//const lista = dicc[0];
//const nombre = lista[1];
//const desc = lista[2];



  //view.push(aux)



class Contenedor extends React.Component {

  render() {


    return create("body", {}, 
      create("div",{key: id, className: "flip-card"},
      create("div",{ className: "flip-card-inner"},
      create("div",{ className: "flip-card-front"},nombreBueno),
      create("div", {className: "flip-card-back"},
      create('h3',{className:'Logo'},desc)))),


);
    
  }
}



const domContainer = document.querySelector('#caja');
const root = ReactDOM.createRoot(domContainer);
root.render(create(Contenedor));