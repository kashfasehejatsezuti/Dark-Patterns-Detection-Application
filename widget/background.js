chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'getDataFromStorage') {
        chrome.storage.local.get(["patternType"], (data) => {
            // Send the data back to the content script
            sendResponse(data);
        });
        return true;
    }
  });
  
  chrome.runtime.onMessage.addListener((message, sender, sendResponse)=>{
    if(message.action==='updateDatainStorage'){
      chrome.storage.local.set({["patternType"]:message.data}, ()=>{
        console.log("data updated");
      })
    }
  })