'use strict';

const build = React.createElement;

class List extends React.Component {

    render (){
        return build(
            "div", {},
            build("h1", {className: "Title"}, "This is the list of private booths"),
            
        );
    }
}    

const domContainerBody = document.querySelector('#list');
const rootBody = ReactDOM.createRoot(domContainerBody);
rootBody.render(build(List));