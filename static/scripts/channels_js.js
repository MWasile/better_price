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
            'message': `${user_input}`
        }));

    });


})

function organizeWebsocketRespone(data) {
    const data_from_backend = JSON.parse(data)

    switch (data_from_backend.category) {
        case '1':
            clearTrash()
            loadingWheel(true)
            break;
        case '2':

            const bookstores = (JSON.parse(data_from_backend.text))
            bookstores.forEach((es) => {
                const x = new Email(es, data_from_backend.user)
                x.run()
            })
            loadingWheel(false)
            break;
        case '3':
        // console.log(data_from_backend)
        default:
            break;
    }

}


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

class Email {
    constructor(bookStore, user) {
        this.ebookName = bookStore.web_bookstore
        this.ebookAuthor = bookStore.web_author
        this.ebookTitle = bookStore.web_title
        this.ebookPrice = bookStore.web_price
        this.ebookUrl = bookStore.web_url
        this.ebookImage = bookStore.web_image_url
        this.user = user
    }


    creaate_element() {
        const divOne = document.createElement('div')
        const divTwo = document.createElement('div')
        const img = document.createElement('img')
        const divThree = document.createElement('div')
        const h5 = document.createElement('h5')
        const pOne = document.createElement('p')
        const pTwo = document.createElement('p')
        const mainDiv = document.createElement('div')
        const btn = document.createElement('a')

        divOne.className = 'flex justify-start'
        divTwo.className = 'flex flex-col md:flex-row md:max-w-xl rounded-lg bg-gray-400 shadow-lg'
        img.className = 'w-full max-h-48 object-fill md:w-48 rounded-t-lg md:rounded-none md:rounded-l-lg'

        if (this.ebookImage) {
            img.src = this.ebookImage
        }
        divThree.className = 'p-6 flex flex-col justify-start'
        h5.className = 'text-gray-900 text-xl font-medium mb-2'
        h5.innerHTML = this.ebookTitle
        pOne.className = 'text-gray-700 text-base mb-4'
        pOne.innerHTML = this.ebookPrice + ' $'
        pTwo.className = 'text-gray-600 text-xs'
        pTwo.innerHTML = this.ebookAuthor
        mainDiv.className = 'flex items-start p-4 mt-12 mx-auto lg:px-12 lg:w-3/5 gap-2'

        btn.href = this.ebookUrl
        btn.innerHTML = `Go to ${this.ebookName}!`

        divThree.appendChild(h5)
        divThree.appendChild(pOne)
        divThree.appendChild(pTwo)
        divThree.appendChild(btn)


        divTwo.appendChild(img)
        divTwo.appendChild(divThree)

        divOne.appendChild(divTwo)
        mainDiv.appendChild(divOne)

        const result = document.querySelector('#results')
        result.appendChild(mainDiv)


    }

    run() {
        this.creaate_element()
    }
}