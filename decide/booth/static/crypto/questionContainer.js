'use strict';

import './style.css'

const e = React.createElement;

class QuestionContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    if (this.state.liked) {
      return 'Saldrá el texto de la votación';
    }

    return e(
      'button',
      { onClick: () => this.setState({ liked: true }) },
      'A cambiar por el texto de la votación'
    );
  }
}

const domContainer = document.querySelector('#questionContainer');
const root = ReactDOM.createRoot(domContainer);
root.render(e(QuestionContainer));