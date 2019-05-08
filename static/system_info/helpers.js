'use strict';

var start_update_info_task = function(connections) {
    $.ajax({
        type: 'POST',
        url: '/system_info/',
        data: JSON.stringify(connections)
    });
};

var update_my_info = function() {
    alert('Это заглушка )\n' +
            'Воспользуйтесь функцией start_update_info_task(comps)' +
            ' для запуска обновления конфигураций.\nНайти эту функцию' +
            ' можно в /system_info/');
    var ip = $('input#id_localip').val();
    var count = parseInt($('input#id_comp_count').val());
    var password = '';
    var admin = '';
    var comps = [];
    for (var i = 1; i <= count; ++i) {
        comps.push({
            ip: ip + i,
            password: password,
            admin: admin
        });
    }
    console.log(comps);
    start_update_info_task(comps);
    return false;
};


var launch_bootbox = function(url_, defaults_, title_, options) {
    defaults_ = defaults_ || {};
    options = options || {};
    var add_script = '<script>';
    $.each(defaults_, function(i, e) {
        add_script += '$("select#id_'+i+'").val('+e+');';
    });
    add_script += '</script>';
    $.ajax({
        url: url_,
        type: 'GET',
        success: function(content_) {
            var content = content_ + add_script;
            console.log(options, options.className || "modal-st");
            var box = bootbox.dialog({
                message: content,
                className: options.className || "modal-st",
                title: title_ || 'Создать новый сервис',
                onEscape: true,
                closeButton: true,
                backdrop: options.backdrop || true,
                buttons: options.buttons || {
                    main: {
                        label: "<span class=\"glyphicon " + (options.savecls || "glyphicon-floppy-disk") +
                        "\" style=\"margin-left:2px\"></span>" +
                        (options.save || "Сохранить"),
                        className: "btn-success",
                        callback: options.saveCallback || function () {
                            $("#new_popup_form").submit();
                        }
                    },
                    close: {
                        label: "<span class=\"glyphicon glyphicon-remove\" style=\"margin-left:2px\"></span>"+
                        (options.close || "Закрыть"),
                        className: "btn-danger",
                        callback: function() {}
                    }
                }
            });
            box.on('shown.bs.modal', function () {
                if (typeof options.on_show === 'function') {
                    return options.on_show();
                }
            });
        }
    });
};


function SelectText(element) {
    var doc = document
        , text = element
        , range, selection
    ;
    if (doc.body.createTextRange) {
        range = document.body.createTextRange();
        range.moveToElementText(text);
        range.select();
    } else if (window.getSelection) {
        selection = window.getSelection();
        range = document.createRange();
        range.selectNodeContents(text);
        selection.removeAllRanges();
        selection.addRange(range);
    }
}