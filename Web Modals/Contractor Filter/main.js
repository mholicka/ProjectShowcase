
// function to create JS objects from the coldfusion database calls.
var queryToObject = function(q) {
    var col, i, r, _i, _len, _ref, _ref2, _results;
    _results = [];
    for (i = 0, _ref = q.ROWCOUNT; 0 <= _ref ? i < _ref : i > _ref; 0 <= _ref ? i++ : i--) {
        r = {};
        _ref2 = q.COLUMNS;
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
            col = _ref2[_i];
            r[col.toLowerCase()] = q.DATA[col][i];
        }
        _results.push(r);
    }
    return _results;
};

// cfc is declared.
searchCFC = new searchCFC();
searchCFC.setHTTPMethod('GET');

var companyInfo = {};
var textfield;

// the rows are made as objects.
function makeRows(data) {
    var companyInfo_temp = {};
    var compTrades = [];
    $.each(data, function(idx) {
        var obj = data[idx];
        var keys = Object.keys(obj);
        var row = {};
        keys.forEach(function(key) {
            if (!(["trade_id"].includes(key)))
                row[key] = obj[key];
        });
        if (!(row.companyname in companyInfo_temp)) {
            compTrades = [];
            if (row.other !== null) compTrades.push(row.other);
            if (row.trd_name!='Other') compTrades.push(row.trd_name);
            companyInfo_temp[row.companyname] = {
                name: row.companyname,
                expertise: compTrades,
                city: row.city,
                province: row.province,
                id: row.contract_id,
                prequalstatus: row.prequalstatus,
                submit_date: row.submitdate,
                numComments: row.numcomments

            };
          // trades are added to thier own array to be stored.
        } else {
            if (!(compTrades.includes(row.trd_name)) && !(compTrades.includes(row.other))) {
                if (row.trd_name!='Other') compTrades.push(row.trd_name);
            }
        }
        // some db fields are not to be shown in the table. These are taken out of the object which will be
        // sent to the table creation function.
        var remove = ['id', 'prequalstatus', 'numComments'];
        textfield = Object.getOwnPropertyNames(companyInfo_temp[row.companyname]);
        for (var rm of remove) {
            if (textfield.indexOf(rm) > -1) textfield.splice(textfield.indexOf(rm), 1);
        }

    });

    // throw new Error("Stopping Execution... Check Output");
    companyInfo = companyInfo_temp;
    return companyInfo_temp;

}
// makes the checkboxes based on the different types.
function make_checkboxes(type, cid, cname) {
    var checkbox = document.createElement("INPUT");
    checkbox.type = "checkbox";
    checkbox.setAttribute('value', type + '_' + cname);
    checkbox.setAttribute('id', type + "_" + cid);
    return checkbox;

}

// the checkboxes are assigned classes and propeties based
// on the type of checkbox it is (accept/reject/archive (was talked about,not implemented yet)).
function assignCheck(status, tr, cid) {
    var assign = {};
    switch (parseInt(status)) {
        case 2:
            assign.class = 'success';
            assign.nothired = 'disabled';
            assign.hired = 'checked';
            assign.archived = 'disabled';
            break;
        case 3:
            assign.class = 'danger';
            assign.nothired = 'checked';
            assign.hired = 'disabled';
            assign.archived = 'disabled';
            break;
        case 9:
            assign.class = 'info';
            assign.nothired = 'disabled';
            assign.hired = 'disabled';
            assign.archived = 'checked';
            break;
            // default:


    }
    $(tr).addClass(assign.class);
    $('#nothired_' + cid).prop(assign.nothired, true);
    $('#hired_' + cid).prop(assign.hired, true);
}
// making the window.
function openWin(windowURL, windowName, windowFeatures) {
    window.open(windowURL, windowName, windowFeatures);
}
var acc_done = false;

// the table is populated based on the objects it takes in.
function populateTable(data, tableCd) {
    if (!acc_rej) {
        $('#contractTable').empty();
    }
    var tbl = $('#contractTable');

    var btn = document.createElement("BUTTON");
    var comments = document.createElement("BUTTON");
    var t = document.createTextNode("View");
    data = queryToObject(data);
    sData = JSON.stringify(data);
    // throw new Error("Stopping Execution... Check Output");
    var companyReturn = makeRows(data);

    // buttons and checkboxes are declared. will be made into columns later.
    var buttons = ["comments", "full_info"];
    var checkboxes = ["accept", "reject"];
    tbl.append('<thead><tr></tr></thead>');
    colNames = textfield.concat(buttons).concat(checkboxes);


    // based on the column type (checkboxes), the column is populated.
    $thead = $('#contractTable > thead > tr:first');
    if ((acc_rej && !acc_done) || !acc_rej) {
        for (var i = 0, len = colNames.length; i < len; i++) {
            if (colNames[i].includes('_')) colNames[i] = colNames[i].replace('_', ' ');
            if (i === len - 2) $thead.append('<th id ="accept">' + colNames[i] + '</th>');
            else if (i === len - 1) $thead.append('<th class="acc_rej">' + colNames[i] + '</th>');
            else if (textfield[i] != 'id') $thead.append('<th>' + colNames[i] + '</th>');

        }
        acc_done = true;
    }

  // for each row, each column is made.
    $.each(companyReturn, function(company) {
        var tr = $('<tr/>').appendTo(tbl);
        tr.attr('align', 'center');
        var companyDetails = companyReturn[company];
        companyDetails.comments = comments;
        companyDetails.full_info = btn;
        companyDetails.accept = 'hired';
        companyDetails.reject = 'nothired';

        // for each propertyName, the column is made.
        for (var propertyName in companyDetails) {
            var td;
            // if it is a textfield , the object is appended to the column in that row.
            if (textfield.includes(propertyName)) {
                td = $('<td/>').appendTo(tr);
                var x = (propertyName == 'expertise') ? td.append(companyDetails[propertyName].join(', ')) : td.append(companyDetails[propertyName]);

            // if the column is a checkbox or a button, it is made.
            } else if (buttons.concat(checkboxes).includes(propertyName)) {
                td = $('<td/>').appendTo(tr);
                if (propertyName == 'reject') td.addClass('acc_rej');
                if (propertyName == 'full_info' || propertyName == 'comments') {
                    btn = document.createElement("a");
                    btn.setAttribute("class", "all-info btn btn-success");
                    if (propertyName == 'full_info') {
                        t = document.createTextNode("View");
                        btn.appendChild(t);
                        btn.setAttribute("onclick", "openWin(" + "'allinfo.cfm?id=" + companyDetails.id + "'," + "'All Info', 'width=1000,height=500,toolbar=0,location=0,directories=0,status=0,menuBar=0,scrollBars=1,resizable=1' ); newWindow.focus();");
                    } else {
                        t = document.createElement("i");
                        // t.setAttribute("class", "fa fa-list-alt");
                        t.setAttribute("class", "fa fa-comment-o");
                        t.setAttribute("aria-hidden", "true");
                        btn.setAttribute("onclick", "openWin(" + "'comments.cfm?id=" + companyDetails.id + "'," + "'Comments', 'width=500,height=800,toolbar=0,location=0,directories=0,status=0,menuBar=0,scrollBars=1,resizable=1' ); newWindow.focus();");
                        if (companyDetails.numComments > 0) t.setAttribute("class", "fa fa-comment");
                        btn.appendChild(t);


                    }
                    // button is assigned to the column
                    td.append(btn);

                } else if (!acc_rej && (checkboxes.includes(propertyName))) {
                    var check = make_checkboxes(companyDetails[propertyName], companyDetails.id, companyDetails.name);
                    td.append(check);

                } else {
                    $('.acc_rej').remove();
                    $('#accept').text("Type");
                    td.append(document.createTextNode(tableType(tableCd)));
                }

            }

        }
        assignCheck(companyDetails.prequalstatus, tr, companyDetails.id);

    });

    checkHandler();
    // throw new Error("Stopping Execution... Check Output");

}
// the tabletype will be used to get all the needed info from the database.
function tableType(tableID) {
    var ret;
    switch (parseInt(tableID)) {
        case 1:
            ret = "Consultant";
            break;
        case 2:
            ret = "Supplier";
            break;
        case 3:
            ret = "reject";
            break;
        case 4:
            ret = "accept";
            break;
        default:
            ret = "Contractor";
    }
    return ret;


}

// whenever the checkbox is clicked, then the handler is used to store it in into the database.
// it can be either accepted, or rejected, and this repliacted in the database.
function checkHandler() {
    $('input[type=checkbox]').change(function() {

        var val = $(this).prop('value').split('_')[0];
        var class_set = ($(this).prop('value').split('_')[0] == 'hired' ? 'success' : 'danger');
        var tmp = $(this).prop('id').split('_')[1];
        var other = ($(this).prop('value').split('_')[0] == 'hired' ? '#nothired_' + tmp : '#hired_' + tmp);
        var vendorName = $(this).prop('value').split('_')[1];
        var curTR = $(this).parent().parent();
        if ( $(this).is(':checked')) {
          // if the checkbox is checked, and value is hired, the status is changed in the db to be accepted.
          // same for denied.
            if (val == 'hired') {
                companyInfo[vendorName].prequalstatus = 2;
            } else {
                companyInfo[vendorName].prequalstatus = 3;
            }

            curTR.addClass(class_set);
            // to reduce confusion in the table, the other checkbox is disabled.
            $(other).attr('disabled', 'disabled');
        } else {
            // if a checkbox is already checked and checked again, the other is re-enabled and the style is revereted to the original.
            curTR.removeClass(class_set);
            $(other).removeAttr("disabled");
            companyInfo[vendorName].prequalstatus = 1;

        }
        // finally, the database is updated.
        searchCFC.updVendors(companyInfo[vendorName].id, companyInfo[vendorName].prequalstatus);

    });
}

// on page load, the tables are populated based on their types. Selectize allows us th filter all the tables based on the filters.
// if the table type is accepted/rejected, we cannot filter it as there are 3 tables merged into one because we need to see all the
//different types of vendors and this was the fastest way i could think of to do it.. might need to be looked at again and mode better.
var acc_rej;
$(function() {
    var tableCode = parseInt($('#tableID').val());
    // accepted/rejected table, so the tables are all made in a loop and added .
    if (tableCode === 3 || tableCode === 4) {
        acc_rej = true;
        for (var x in [0, 1, 2]) {
            var ret = searchCFC.getContractors_filtered($('#cName').val(), $('#trd').val(), $('#loc').val(), $('#city').val(), tableType(parseInt(x)), tableCode);

            if (ret.ROWCOUNT > 0) {
                populateTable(ret, x);
            }

        }
      // if the table type is a specific vendor type. this is made.
    } else {
        populateTable(searchCFC.getContractors_filtered($('#cName').val(), $('#trd').val(), $('#loc').val(), $('#city').val(), tableType(tableCode)), "");

          $('select').selectize({
            onChange: function(query) {
                if (!query.length) return;
                populateTable(searchCFC.getContractors_filtered($('#cName').val(), $('#trd').val(), $('#loc').val(), $('#city').val(), tableType(tableCode)), "");
            }

        });

    }
    
    // ('select').on("click",function(){
    //
    // });

});
