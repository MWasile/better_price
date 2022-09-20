document.addEventListener("DOMContentLoaded", function() {

    const ebookSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/test'
    );

    ebookSocket.onmessage = function (e) {
        organizeWebsocketRespone(e.data)
    };

    ebookSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };


    const user_btn = document.querySelector("#user-btn");

    user_btn.addEventListener("click", () =>{
        const user_input = document.querySelector('#user-input').value


        ebookSocket.send(JSON.stringify({
            'massage': `${user_input}`
        }));

    });



})

function organizeWebsocketRespone(data){
    const data_from_backend = JSON.parse(data)

    switch (data_from_backend.massage){
        case 1:
            break;
        case 2:
            console.log(data_from_backend.data)
            break;
        case 3:
            break
        default:
            console.log('chuj tu nocuje')
    }

}

