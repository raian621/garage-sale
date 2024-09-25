console.log("checkout.js loaded")
/** @type {HTMLInputElement} */
const searchBox = document.querySelector("#search_box")
const searchResultsBox = document.querySelector("#search_results")

searchBox.addEventListener("input", (e) => {
  console.log(e.target.value)
  searchItems(e.target.value)
})
var searchResults = []
var cart = []

/** @param {string} name */
async function searchItems(name) {
  if (name.length == 0) {
    searchResults = []
    renderSearchResults()
    return
  }
  try {
    const res = await fetch(`/shop/search/?name=${name}`)
    if (res.ok) {
      searchResults = await res.json()
    } else {
      searchResults = []
    }
    renderSearchResults()
  } catch(error) {
    console.error(error)
  }
}

/** @param {any[]} results */
function renderSearchResults() {
  searchResultsBox.replaceChildren(...searchResults.map((result, i) => { 
    const resultElement = document.createElement("button")
    resultElement.addEventListener("click", (e) => handleClickSearchResult(e, i)) 
    resultElement.innerText = result.fields.name
    resultElement.setAttribute("key", i)
    resultElement.className = "dropdown-item"
    return resultElement
  }))
}

function handleClickSearchResult(e, i) {
  e.preventDefault()
  addToCart(searchResults[i])
  renderSearchResults()
}

function addToCart(item) {
  cart.push(item)
  renderCart()
}

function renderCart() {
  if (cartElement === undefined) {
    var cartElement = document.querySelector("#cart_items")
    
    if (cartElement === undefined) {
      console.error("cart element not found")
    }
  }

  cartElement.replaceChildren(...cart.map(item => itemCard(item)))
}

function itemCard(item) {
  const itemElement = document.createElement("div")
  itemElement.className = "p-3 d-flex gap-3 border border-primary rounded"
  const itemName = document.createElement("h3")
  const itemDescription = document.createElement("p")
  itemName.innerText = item.fields.name
  itemDescription.innerText = item.fields.description
  const innerElement = document.createElement("div")
  innerElement.appendChild(itemName)
  innerElement.appendChild(itemDescription)
  itemElement.appendChild(innerElement)

  return itemElement
}
