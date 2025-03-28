const menu = document.getElementById("menu")
const cartBtn = document.getElementById("cart-btn")
const cartModal = document.getElementById("cart-modal")
const cartItemsContainer = document.getElementById("cart-items")
const cartTotal = document.getElementById("cart-total")
const checkoutBtn = document.getElementById("checkout-btn")
const closeModalBtn = document.getElementById("close-modal-btn")
const cartCounter = document.getElementById("cart-count")
const addressInput = document.getElementById("address")
const addressWarn = document.getElementById("address-warn")

const homePickupRadio = document.getElementById('home-pickup');
const localPickupRadio = document.getElementById('local-pickup');

let cart = [];
let totalGlobal = 0;

// Abrir o modal  do carrinho
cartBtn.addEventListener("click", function () {
    updateCartModal();
    cartModal.style.display = "flex"
})

// Fechar o modal Cart quando clicar em "fechar"
closeModalBtn.addEventListener("click", function () {
    cartModal.style.display = "none"
})


// Fechar o modal Cart quando clicar fora
cartModal.addEventListener("click", function (event) {
    if (event.target == cartModal) {
        cartModal.style.display = "none"
    }
})

// Função para detectar o click no carrinho e chamar a função addToCart
menu.addEventListener("click", function (event) {
    let parentButton = event.target.closest(".add-to-cart-btn")
    const name = parentButton.getAttribute("data-name")
    const price = parseFloat(parentButton.getAttribute("data-price"))

    addToCart(name, price)
})


// Função para adicionar ao carrinho
function addToCart(name, price) {
    // Verifica se o item já existe na lista
    const existingItem = cart.find(item => item.name === name)

    // Se o item já existe, aumenta apenas a quantidade em +1
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            name,
            price,
            quantity: 1
        })
    }

    Toastify({
        text: "Item adicionado ao carrinho!",
        duration: 3000,
        close: true,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        style: {
            background: "#22c55e",
        },
    }).showToast();

    updateCartModal()
}

// Atualiza o carrinho
function updateCartModal() {
    cartItemsContainer.innerHTML = "";
    let totalLocal = 0;

    cart.forEach(item => {
        const cartItemElement = document.createElement("div");
        cartItemElement.classList.add("flex", "justify-btwenn", "mb-4", "flex-col")

        cartItemElement.innerHTML = `
        <div class="flex items-center justify-between">
            <div>
                <p class="font-bold"> ${item.name}</p>
                <p>Qtd: ${item.quantity}</p>
                <p class="font-medium mt-2">R$ ${item.price.toFixed(2)}</p>
            </div>

            
            <button class="remove-btn" data-name="${item.name}">
                Remover
            </button>
            
        </div>
        `
        // Calcula o total
        totalLocal += item.price * item.quantity;
        cartItemsContainer.appendChild(cartItemElement)
    })

    //Atualiza a variavel global com o valor do total
    totalGlobal = totalLocal;

    // Converse para Reais 
    cartTotal.textContent = totalLocal.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });

    cartCounter.innerHTML = cart.length;
}


// Função para chamar a função de remover o item do carrinho
cartItemsContainer.addEventListener("click", function (event) {
    if (event.target.classList.contains("remove-btn")) {
        const name = event.target.getAttribute("data-name")

        removeItemCart(name);

        Toastify({
            text: "Item removido do carrinho!",
            duration: 3000,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#ef4444",
            },
        }).showToast();
    }
})

// Função para remover o item do carrinho
function removeItemCart(name) {
    const index = cart.findIndex(item => item.name === name);

    if (index !== -1) {
        const item = cart[index];
        if (item.quantity > 1) {
            item.quantity -= 1;
            updateCartModal();
            return;
        }

        cart.splice(index, 1);
        updateCartModal();
    }
}

// Função para verificar se algo está sendo escrito no input address
//e retirar o erro de endereço
addressInput.addEventListener("input", function (event) {
    let inputValue = event.target.value;

    if (inputValue !== "") {
        addressInput.classList.remove("border-red-500")
        addressWarn.classList.add("hidden")
    }
})

// Finalizar pedido
checkoutBtn.addEventListener("click", function () {

    //Confere se o restaurante está aberto
    const isOpen = checkRestaurantOpen();
    if (!isOpen) {
        Toastify({
            text: "Ops, o restaurante está fechado!",
            duration: 3000,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#ef4444",
            },
        }).showToast();

        return;
    }

    // Confere se tem itens no carrinho
    if (cart.length === 0) return;



    // Confere se a opção de receber em casa está marcada
    if (!document.getElementById('local-pickup').checked) {
        // Confere se o endereço é diferente de vazio
        if (addressInput.value === "") {
            // Verifica se a opção "Receber em casa" está marcada
            if (document.getElementById('home-pickup').checked) {
                addressWarn.classList.remove("hidden");
                addressInput.classList.add("border-red-500");
                return;
            }
        }
    }

    // Confere se a opção de receber em casa ou local está marcada
    if (!document.getElementById('home-pickup').checked && !document.getElementById('local-pickup').checked) {
        Toastify({
            text: "Por favor, selecione a forma de entrega!",
            duration: 3000,
            close: true,
            gravity: "top",
            position: "right",
            stopOnFocus: true,
            style: {
                background: "#ef4444",
            },
        }).showToast();
        return;
    }

    // Finaliza o pedido e encaminha pro wpp
    const cartItems = cart.map((item) => {
        return (
            `${item.name} Quantidade: (${item.quantity}) Preço: R$${item.price} |`
        )
    }).join(" ")

    const message = encodeURIComponent(`${cartItems}  
*Total: R$${totalGlobal}* |`);
    const phone = "+5521974857727"

    window.open(`https://wa.me/${phone}?text=${message} *Endereço: ${addressInput.value}*`, "_blank")

    cart = [];
    updateCartModal();
})


// Verifica a hora
function checkRestaurantOpen() {
    const data = new Date();
    const hora = data.getHours();

    return hora >= 18 && hora <= 23; //true = restaurante está aberto
}

const spanItem = document.getElementById("date-span")
const isOpen = true;

// Manipula o card 
if (isOpen) {
    spanItem.classList.remove("bg-red-500");
    spanItem.classList.add("bg-green-600")
} else {
    spanItem.classList.remove("bg-green-600")
    spanItem.classList.add("bg-red-500")

}

// Event listener para os radio buttons
homePickupRadio.addEventListener('change', () => {
    addressInput.style.display = homePickupRadio.checked ? 'block' : 'none';
});


localPickupRadio.addEventListener('change', () => {
    addressInput.style.display = localPickupRadio.checked ? 'none' : 'block';
    addressInput.value = ''; // Limpa o campo de endereço se "Buscar no local" for selecionado
});

