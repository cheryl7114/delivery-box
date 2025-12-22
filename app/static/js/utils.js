// Universal message display function
function showMessage(elementId, messageData) {
    const messageDiv = document.getElementById(elementId)
    
    // Extract message and type from data
    const message = messageData.message || messageData.error || 'An error occurred'
    const type = messageData.type || 'error' // Default to error if not specified
    
    const colors = {
        error: 'bg-red-100 border-red-400 text-red-700',
        success: 'bg-green-100 border-green-400 text-green-700',
        warning: 'bg-yellow-100 border-yellow-400 text-yellow-700',
        info: 'bg-blue-100 border-blue-400 text-blue-700'
    }
    
    messageDiv.innerHTML = `
        <div class="${colors[type]} border px-4 py-3 rounded-xl relative" role="alert">
            <span class="block sm:inline">${message}</span>
            <span class="absolute top-0 bottom-0 right-0 px-4 py-3 cursor-pointer" onclick="this.parentElement.remove()">
                <svg class="fill-current h-6 w-6" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
                </svg>
            </span>
        </div>
    `
}

// Clear message
function clearMessage(elementId) {
    document.getElementById(elementId).innerHTML = ''
}