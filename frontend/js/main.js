// Drag and drop events
jQuery(function ($) {
    function $(id) {
        return document.getElementById(id);
    }

    dragula([$('drag-elements'), $('drop-target')]);
});

//All Events handling
jQuery(function ($) {
    let quest = $('input#question');

    $("input:checkbox").on('change', function () {
        if (this.checked) {
            $(this).closest("label").addClass('bg-primary text-white');
            if (this.id === "addQuestion") {
                $('.formulateQuestionGroup').show();
                quest.prop('required', true);
            }
        } else {
            $(this).closest("label").removeClass('bg-primary text-white');
            if (this.id === "addQuestion") {
                if (quest.is(':visible')) {
                    quest.prop('required', false);
                    quest.val('');
                }
                $('.formulateQuestionGroup').hide();
            }
        }
    });

    const $form = $("#mainForm");
    const $displayResult = $("#fileResult");

    // On User press submit actions
    $form.on('submit', function (e) {
        e.preventDefault();

        let serviceArray = [];
        $('div.predefinedPipeline').children('div.service-order').each(function (i, elm) {
            serviceArray.push($(this).data('serviceOrder'));
        });

        let data = $(this).serializeArray();

        let objIndex = data.findIndex((obj => obj.name === "hashtags"));
        let newValue = (data[objIndex].value).split(',');
        data[objIndex].value = newValue;

        data.push({name: 'serviceOrder', value: serviceArray});
        let jsonObject = JSON.stringify(data, null, 2);
        download(jsonObject);
    })

    // Create Blob, call download file
    function download(jsonObject) {
        // let result = runPyScript(jsonObject);
        let blob = new Blob([jsonObject], {type: 'text/plain;charset=UTF-8'});
        downloadFile(blob, "yamlConfiguration.json");
    }

    // Download
    function downloadFile(blob, filename) {
        let url = null;
        url = window.URL.createObjectURL(blob);
        let link = document.createElement("a")
        link.download = filename;
        link.innerText = 'Download Yaml configuration';
        link.href = url;
        link.classList.add("downloadLink");
        $displayResult.append(link);
        link.click();
        link.remove();
    }
});
