'use strict';

const create = React.createElement;
const MyReactComponent = (props) => {
  const { message } = props;
  // Use the message prop in your component here
};


class Contenedor extends React.Component {
  

  render() {


    return React.createElement('h1', message);
  }
}

const domContainer = document.querySelector('#contenedor');
const root = ReactDOM.createRoot(domContainer);
root.render(create(Contenedor));