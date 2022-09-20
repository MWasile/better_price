document.addEventListener("DOMContentLoaded", function() {
    const ebookSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/test'
    );

    ebookSocket.onmessage = function (e) {
        console.log(e.data)

    };

    ebookSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };




    const user_btn = document.querySelector("#user-btn")

    user_btn.addEventListener("click", () =>{
        const user_input = document.querySelector('#user-input').value


        ebookSocket.send(JSON.stringify({
            'massage': `${user_input}`
        }))

    })



})