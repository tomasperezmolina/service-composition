var $form=$("#mainForm");
//var $hashtags = $("#hushtagsArea");
var $displayResult = $("#fileResult");

// On User press submit actions
$form.on('submit', function (e) {
    e.preventDefault();
    let jsonObject = collectFormdata();
    download( jsonObject );
})

// Correct form data and return as Json object
function collectFormdata() {
    var elements = document.querySelector('#mainForm').elements;
    var obj ={};
    for(var i = 0 ; i < elements.length ; i++){
        var item = elements.item(i);
        obj[item.name] = item.value;
    }
     return JSON.stringify(obj);
}

// Create Blob, call download file
function download( jsonObject){
    var blob= new Blob([jsonObject], {type:'text/plain;charset=UTF-8'});
    downloadFile( blob, "yamlConfiguration.json");
}

//
function downloadFile( blob, filename ){
    let url = null;

    /*    if ( $("#hushtagsArea") ) {
        URL.revokeObjectURL( url);
    }*/

    url = window.URL.createObjectURL(blob);

    let link = document.createElement("a")
    link.download = filename;
    link.innerText = 'Download Yaml configuration';
    link.href = url;
    link.classList.add("downloadLink");
    $displayResult.append(link);
    link.click();
    link.remove();  // improve this-remove a for 2d click and create new
}

