const info=document.getElementById("info")
const h1=document.getElementById("title")
const h2=document.getElementById("title")
const ima=document.getElementById("images")
async function abcd(){
    const blob=await fetch(`https://meme-api.com/gimme`)
    data =await blob.json()
    h1.innerText=data.title
    info.innerText=data.subreddit
    ima.src=data.url
    

   
}
