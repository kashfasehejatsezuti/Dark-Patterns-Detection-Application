let imageData = [];

window.addEventListener("DOMContentLoaded", (event) =>{
    const el = document.getElementById("submitpat");
    if(el){
        el.addEventListener('click', processInput, false);
    }
})

window.addEventListener("DOMContentLoaded", (event)=>{
    const imgel = document.getElementById("capture");
    if(imgel){
        imgel.addEventListener("click", captureImage, false)
    }
})

window.addEventListener("DOMContentLoaded", (event) => {
    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("patternRemove")) {
            const patternTime = event.target.dataset.patternTime;
            removePattern(patternTime);
        }
    });
});

window.addEventListener("DOMContentLoaded", (event) => {
    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("removeImage")) {
            const patternTime = event.target.dataset.patternTime;
            removeImage(patternTime);
        }
    });
});

const getData = async () => {
    const key = 'patternType'
    let patterns = await new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const patterns = result.patternType ?? [];
            resolve(patterns)
        });
    });
    const updatedPatterns = patterns || [];
    const patternList = document.getElementById("patternobj-list");
    if(Array.isArray(imageData)){
        updatedPatterns.forEach(element => {
            const listItem = document.createElement("div");
            listItem.className = "patternItemsDiv";
            // listItem.textContent = `Type: ${element.patternType}, description: ${element.patternDesc}`
            listItem.innerHTML = `
                <div style="display:flex; align-items:center; color:azure;">
                    <h3>${element.patternType}</h3>
                    <i class="material-icons patternRemove" data-pattern-time="${element.patternTime}" style="cursor:pointer;">delete</i>
                </div>
                <p style="color:azure;">${element.patternDesc}</p>
            `;
            element.patternimages.forEach(image=>{
                const imgItem = document.createElement("div");
                imgItem.innerHTML = `
                    <div style="margin: 2px;">
                        <img src="data:image/png;base64,${image.file_base64}" width="200" />
                    </div>
                `
                listItem.appendChild(imgItem);
            })
            patternList.appendChild(listItem)
        });
    }
}

async function processInput() {
    let typeInput = document.getElementById("patterntype").value;
    let currentUrl = await new Promise((resolve,reject) =>{
        chrome.tabs.query({currentWindow: true, active: true}, tabs => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            }
            let urlInput = tabs[0].url;
            resolve(urlInput)
        });
    })
    let descInput = document.getElementById("patterndesc").value;
    let tempImages = await new Promise((resolve, reject) => {
        chrome.storage.local.get("snapshots", (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const patterns = result.snapshots ?? [];
            resolve(patterns)
        });
    });
    let timeCreated = Date.now();
    if(typeInput===""){
        alert("Please enter a valid pattern type");
        document.getElementById("patterntype").value = "";
        document.getElementById("patterndesc").value = "";
    }
    else{
    const key = 'patternType'
    let patternObj = {
        patternType : typeInput,
        patternUrl : currentUrl,
        patternDesc : descInput,
        patternimages : tempImages,
        patternTime : timeCreated
    }
    let patterns = await new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const patterns = result.patternType ?? [];
            resolve(patterns);
        });
    });
    const updatePatterns = [...patterns, patternObj];

    await new Promise((resolve, reject) => {
        chrome.storage.local.set({ [key]: updatePatterns }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
                alert("Delete some patterns to submit new patterns")
            } 
            resolve(updatePatterns)
        });
    });
    // window.localStorage["patternType"] = "updatePatterns";
    chrome.storage.local.set({ "snapshots": [] }, () => {
        if (chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError);
        } 
    });
    document.getElementById("patterntype").value = "";
    document.getElementById("patterndesc").value = "";
    document.getElementById("patternobj-list").innerHTML = "";
    document.getElementById("screenshotContainer").innerHTML = "";
    getData();
}
}
const removePattern = async (timeStamp) =>{
    const key = "patternType";
    let timeStampNumber = parseInt(timeStamp)
    let patterns = await new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const patterns = result.patternType ?? [];
            resolve(patterns);
        });
    });
    const filteredPatterns = patterns.filter(pattern => {
        return pattern.patternTime !== timeStampNumber;
    });
    await new Promise((resolve, reject) => {
        chrome.storage.local.set({ [key]: filteredPatterns }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            resolve(patterns)
        });
    });
    document.getElementById("patternobj-list").innerHTML=""
    getData();
}

const getImageData = async () => {
    const key = 'snapshots'
    let patterns = await new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const patterns = result.snapshots ?? [];
            resolve(patterns)
        });
    });
    const updatedPatterns = patterns || [];
    const patternList = document.getElementById("screenshotContainer");
    if(Array.isArray(updatedPatterns)){
        updatedPatterns.forEach(element => {
            const listItem = document.createElement("div");
            listItem.innerHTML = `
                <div style="margin: 5px;">
                    <div style="display:flex; justify-content: space-between; color:azure;">
                        <h4>${element.name}</h4>
                        <button class="removeImage" style="padding:2px;" data-pattern-time="${element.timestamp}">remove</button>
                    </div>
                    <img src="data:image/png;base64,${element.file_base64}" width="200" />
                </div>
            `
            patternList.appendChild(listItem)
        });
    }
}

async function captureImage() {
    const screenshotContainer = document.getElementById("screenshotContainer");
    const key = "snapshots";
    const imgObj = await new Promise((resolve,reject) => {
        chrome.tabs.captureVisibleTab(null, {}, function(screenshotDataUrl) {
            const screenshotImage = new Image();
            screenshotImage.src = screenshotDataUrl;
            screenshotImage.onload = function(){
                var canvas = document.createElement("canvas");
                canvas.width = screenshotImage.width;
                canvas.height = screenshotImage.height;
                var ctx = canvas.getContext("2d");
                ctx.drawImage(screenshotImage,0,0);
                var dataUrl = canvas.toDataURL();
                const base64 = dataUrl.replace(/^data:image\/?[A-z]*;base64,/,"");
                let imageObj = {
                    name: "image",
                    timestamp: Date.now(),
                    file_base64: base64.toString()
                }
                resolve(imageObj)
            }
        })
    });
    let screenshots = await new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const snaps = result.snapshots ?? [];
            resolve(snaps);
        });
    });
    const updatedImages = [...screenshots, imgObj]
    await new Promise((resolve, reject) => {
        chrome.storage.local.set({ [key]: updatedImages }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
                alert("Delete some patterns to submit new Images")
            } 
            resolve(updatedImages)
        });
    });
    const patternList = document.getElementById("screenshotContainer");
    patternList.innerHTML = ""
    getImageData();
}

const removeImage = async (timeStamp) =>{
    const key = "snapshots";
    let timeStampNumber = parseInt(timeStamp)
    let images = await new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            const images = result.snapshots ?? [];
            resolve(images);
        });
    });
    const filteredImages = images.filter(img => {
        return img.timestamp !== timeStampNumber;
    });
    await new Promise((resolve, reject) => {
        chrome.storage.local.set({ [key]: filteredImages }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } 
            resolve(images)
        });
    });
    document.getElementById("screenshotContainer").innerHTML=""
    getImageData();
}

document.addEventListener("DOMContentLoaded", function(){
    getData();
    getImageData();
})


