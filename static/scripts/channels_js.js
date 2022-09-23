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
    console.log(data_from_backend)
    switch (data_from_backend.category){
        case '1':
            loadingWheel(true)
            clearTrash()
            break;
        case '2':
            const bookstores = (JSON.parse(data_from_backend.text))
            bookstores.forEach((es) => {
                spawnResult(es)
            })
            loadingWheel(false)
            break;
        case '3':
            // console.log(data_from_backend)
        default:
            console.log('chuj tu nocuje')
    }

}


function spawnResult(bookstore){
    const container = document.createElement('div');

    for (const [key, value] of Object.entries(bookstore)){
        let aItem=document.createElement('a')
        aItem.innerHTML= `${key}: ${value}`
        container.appendChild(aItem)
    }

    const site_place = document.querySelector('#results')
    site_place.appendChild(container)
}

function loadingWheel(flag){
    let spiner = document.querySelector('#spinner')
    if (flag === true){
        spiner.classList.remove('invisible')
    }else{
        spiner.classList.add('invisible')
    }
}
function clearTrash(){
        let trash = document.querySelector('#results')

    while (trash.firstChild){
        trash.removeChild(trash.firstChild)
    }
}