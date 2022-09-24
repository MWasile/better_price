document.addEventListener("DOMContentLoaded", function () {

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

    user_btn.addEventListener("click", () => {
        const user_input = document.querySelector('#user-input').value


        ebookSocket.send(JSON.stringify({
            'massage': `${user_input}`
        }));

    });


})

function organizeWebsocketRespone(data) {
    const data_from_backend = JSON.parse(data)

    switch (data_from_backend.category) {
        case '1':
            break;
        case '2':
            const bookstores = (JSON.parse(data_from_backend.text))
            bookstores.forEach((es) => {
                // spawnResult(es)
                const x = new Email(es, data_from_backend.user)
                x.run()
            })
            break;
        case '3':
        // console.log(data_from_backend)
        default:
            console.log('chuj tu nocuje')
    }

}

// function spawnResult(bookstore) {
//     const container = document.createElement('div');
//
//     for (const [key, value] of Object.entries(bookstore)) {
//         let aItem = document.createElement('a')
//         aItem.innerHTML = `${key}: ${value}`
//         container.appendChild(aItem)
//     }
//
//     const site_place = document.querySelector('#results')
//     site_place.appendChild(container)
// }

function loadingWheel(flag) {
    let spiner = document.querySelector('#spinner')
    if (flag === true) {
        spiner.classList.remove('invisible')
    } else {
        spiner.classList.add('invisible')
    }
}

function clearTrash() {
    let trash = document.querySelector('#results')

    while (trash.firstChild) {
        trash.removeChild(trash.firstChild)
    }
}

class Email{
    constructor(bookStore, user) {
        this.element = bookStore
        this.ebookName = bookStore.web_bookstore
        this.ebookAuthor = bookStore.web_author
        this.ebookTitle = bookStore.web_title
        this.ebookPrice = bookStore.web_price
        this.ebookUrl = bookStore.web_url
        this.user = user
        this.containerToReneder = document.createElement('div')
    }
    setAlertButton(){
        const newBtn = document.createElement('button')
        newBtn.innerHTML = 'Price Alert!'
        return newBtn
    }
    mainView(){
        const container = document.createElement('div');

        for (const [key, value] of Object.entries(this.element)) {
            let aItem = document.createElement('a')
            aItem.innerHTML = `${key}: ${value}`
            container.appendChild(aItem)
            }
        container.appendChild(this.setAlertButton())
        this.containerToReneder.appendChild(container)
    }
    eventSetter(){
        if (this.user){
            console.log('True')
            // add event to btn -> api
        }else{
            console.log('false')
        //    render form
        }

    }
    render(){
        const site_place = document.querySelector('#results')
        site_place.appendChild(this.containerToReneder)
    }
    run(){
        this.mainView()
        this.render()
    }
}