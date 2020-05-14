// Drag and drop events
jQuery(function($) {
    function $(id) {
        return document.getElementById(id);
    }
    dragula([$('drag-elements'), $('drop-target')]);
});

//All Events handling
jQuery(function($) {
   $( "input:checkbox" ).on('change', function(){
       if ( this.checked ){
           $(this).closest("label").addClass('bg-primary text-white');
           if (this.id === "addQuestion" ){
               $('.formulateQuestionGroup').show();
           }
       }
       else{
          $(this).closest("label").removeClass('bg-primary text-white');
           if ( this.id === "addQuestion" ){
               $('.formulateQuestionGroup').hide();
           }
       }
    });

    const $form=$("#mainForm");
    //var $hashtags = $("#hushtagsArea");
    const $displayResult = $("#fileResult");

    // On User press submit actions
    $form.on('submit', function (e) {
        e.preventDefault();
        //  console.log( $( this ).serializeArray());
        // let jsonObject = collectFormdata();
        let jsonObject = JSON.stringify ($( this ).serializeArray());
        download( jsonObject );
    })

    // Create Blob, call download file
    function download( jsonObject ){
        // let result = runPyScript(jsonObject);
        let blob= new Blob([jsonObject], {type:'text/plain;charset=UTF-8'});
        downloadFile( blob, "yamlConfiguration.json");
    }

    // Download
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
});
