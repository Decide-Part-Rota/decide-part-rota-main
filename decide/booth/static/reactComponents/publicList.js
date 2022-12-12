'use strict';

const build = React.createElement;
var userInfo = document.getElementById("userdata").value;

class List extends React.Component {

    render (){

        if(userInfo != 'AnonymousUser'){
            return build(
                "div", {},
                build("h1", {className: "Title"}, "This is the list of public booths"),
                
            );
        } else {
            return build(
                "div", {},
                build("h1", {className: "Title"}, "If you wanto to see this service you need to log in"),
                
            );
        }
    }
}    

const domContainerBody = document.querySelector('#list');
const rootBody = ReactDOM.createRoot(domContainerBody);
rootBody.render(build(List));