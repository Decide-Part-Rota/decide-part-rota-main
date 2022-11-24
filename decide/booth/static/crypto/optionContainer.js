'use strict';

import './style.css'

const e = React.createElement;

class OptionContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    if (this.state.liked) {
      return 'Saldrá el texto de cada opción';
    }

    return e(
      'button',
      { onClick: () => this.setState({ liked: true }) },
      'Aqui saldrán las opciones de las votaciones'
    );
  }
}

const domContainer = document.querySelector('#optionContainer');
const root = ReactDOM.createRoot(domContainer);
root.render(e(OptionContainer));