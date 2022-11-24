'use strict';

const e = React.createElement;

class LikeButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    if (this.state.selected) {
      return 'you have checked this box';
    }

    return e(
      'button',
      { onClick: () => this.setState({ selected: true }) },
        'Select option'
    );
  }
}

const domContainer = document.querySelector('#like-button-root');
const root = ReactDOM.createRoot(domContainer);
root.render(e(LikeButton));