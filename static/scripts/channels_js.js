 const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/test'
        );

chatSocket.onmessage = function(e) {
    console.log(e.data)
    console.log('działaj no')
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};
