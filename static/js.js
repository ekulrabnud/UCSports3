$(document).ready(function() {


    bootstrap_alert_success = function(message) {

        $('#alert').append('<div class="alert alert-success"><a class="close" data-dismiss="alert">×</a><span>' + message + '</span></div>');

        setTimeout(function() {
            $("#alert").empty()
        }, 5000);
    }

    bootstrap_alert_danger = function(message) {

        $('#alert').append('<div class="alert alert-danger"><a class="close" data-dismiss="alert">×</a><span>' + message + '</span></div>');

    }

    var errorCheck = function(data){

        if (data['error'] == 1) 
        {
            bootstrap_alert_danger(data['message']);
        }
        else 
        {
            bootstrap_alert_success(data['message'])
        }
    };


    var updateTable = function(url,newData){
      
        $.post(url,newData,function(data){
        
              if (data['error'] == 1) {
                    bootstrap_alert_danger(data['message']);
                    console.log("error")
                } else {
                    bootstrap_alert_success(data['message'])
                }
        })
    }

    var cellEdit = function(){
        // console.log();

        $('.edit').on('dblclick', function(url) {
           
            var originalValue = $(this).text();
            var rowid = this.parentElement.id;
            var column = this.classList[0];
            var url = this.classList[2];

    
            $(this).addClass('cellEditing');
            $(this).html('<input type="text" value="' + originalValue + '"/>');
            $(this).children().first().focus();

            $(this).children().first().keypress(function(e) {

                if (e.which === 13) {

                    newData = {};
                    newData['id'] = rowid;
                    newData[column] = $(this).val();
                    newData['columnName'] = column;
                 
                    updateTable(url,newData)

                    $(this).parent().text($(this).val());
                    $(this).parent().removeClass('cellEditing');
                };
            });

                $(this).children().first().blur(function() {
                $(this).parent().text(originalValue);
                $(this).removeClass('cellEditing');
            });

        });
    }

 
/**************************************************************************************/

    $.get("/channelGuide", function(data) {
        
        $("#guide").html(data);
        $("#channelGuideTable").DataTable({
            "paging":false,
        });

        // cellEdit();   
    });
/**************************************************************************************/

    $.get("/liveSports", function(data) {

        $("#liveSports").html(data);

        $("#save").prop('disabled',true);
    
        cellEdit();

        var initializeDatePicker = function() {
          
            $('#datePicker').datetimepicker({
                format: 'MM/D/YYYY',
                defaultDate:moment(),
                maxDate: moment().add(6, 'days')
            });

            $('#startTimePicker').datetimepicker({
                format: 'h:mm A',
                defaultDate: moment('01:00', 'HH:mm'),
            });

            $('#endTimePicker').datetimepicker({
                format: 'h:mm A',
                defaultDate: moment('23:00', 'HH:mm'),
                icons: {
                    time: 'glyphicon glyphicon-time'
                }
            });
        };

        initializeDatePicker();

        $("#printHeading").html("UCTV Sports Schedule for " + $('#datePicker').find("input").val());

        $('#submit').click(function() {
         
            $.ajax({
                url: '/liveSports',
                type: 'post',
                dataType: 'html',
                data: $('#liveSportsCalForm').serialize(),
                success: function(data) {

                    $("#liveSportsTable").html(data);
                    $("#printHeading").html("UCTV Sports Schedule for " + $('#datePicker').find("input").val())
                }
            });
        });

        $('#email').click(function() {
        
            $.ajax({
                url: '/email',
                type: 'post',
                dataType: 'html',
                data: $('#liveSportsCalForm').serialize(),
                success: function(data) {

                    var mywindow = window.open("", "Test", "width=800,height=800,resizable,scrollbars=yes,status=1")
                    mywindow.document.write(data);

                }
            });
        });

        $('#pdf').click(function() {

            $("#pdfHeading").html("UCTV Sports Schedule for " + $('#datePicker').find("input").val())
            var page = $("#liveSportsTable").html()
            var date = $('#datePicker').find("input").val()

            json = JSON.stringify({
                page: page,
                date: date
            });
            $.ajax({
                url: '/pdf',
                type: 'POST',
                contentType: "application/json",
                data: json,
                //data: {"pcontent":page},

                success: function(data) {
                    bootstrap_alert_success(data);
                }
            });
        });


        $('#infocast').click(function(){
           
            $.post('/infocast',$('#liveSportsCalForm').serialize(),function(data){

                errorCheck(data);
            });
        });
   
        $('#edit').click(function() {
        
            $.get('/editLiveSports',function(data){
                
                $('#liveSportsTable').empty().html(data);
                $("#save").prop('disabled',false);
            })
        });  


        $('#add').click(function() {
          
            $("#edit_schedule_popup").modal('show');
        });


        $('#add_event_btn').click(function(){

            $.post('/add',$('#add_event').serialize(),function(data){
                 errorCheck(data);
                 console.log(data);
                $("#edit_schedule_popup").modal('hide');

            // $.post('/saveLiveSportsEdit',$('form').serialize(),function(data){
            //      errorCheck(data);
            //     $("#liveSportsTable").empty().append(data);
            //     $("#printHeading").html("UCTV Sports Schedule for " + $('#datePicker').find("input").val())
            //     });
            })
        })

        $('#save').click(function() {

            console.log($('#liveSportsForm').serialize())

          
            $.post('/saveLiveSportsEdit',$('#liveSportsForm').serialize(),function(data){
                errorCheck(data);



                $("#liveSportsTable").empty().append(data['html']);
               
                $("#save").prop('disabled',true);
                $("#printHeading").html("UCTV Sports Schedule for " + $('#datePicker').find("input").val())
            });
        }); 

        $("#reloadSports").click(function(){
           
            bootstrap_alert_success("Updating.........please wait!");
     
            $.get('/reloadSports',function(data){
          
                $("#liveSportsTable").empty().html(data);         
            })
        })
    });
/**************************************************************************************/

    $.get("/crestronLiveSports", function(data) {

        $("#crestronLiveSports").html(data);

        $("#save_crestron_live_sports").prop('disabled', true);

        $("#edit_crestron_live_sports").click(function() {

            $("#save_crestron_live_sports").prop('disabled', false);

            $.get('/editCrestronLiveSports', function(data) {

                $("#crestronLiveSportsTable").empty().html(data);

            });
        });


        $("#save_crestron_live_sports").click(function() {

            $.post('/editCrestronLiveSports', $('#crestron_live_sports_form').serialize(), function(data) {

                errorCheck(data);
                $("#crestronLiveSportsTable").empty().html(data);
                $("#save_crestron_live_sports").prop('disabled', true);
            });
        });

        $("#reload_crestron_live_sports").click(function() {
            console.log('reload_click');

            $.get('/crestronLiveSportsReload', function(data) {

                $("#crestronLiveSportsTable").empty().html(data);
            });


        });

        $("#update_crestron_live_sports").click(function() {
            console.log('update');

            $.get('/crestronLiveSportsUpdate', function(data) {
                console.log(data);
                errorCheck(data);
            });

        });

    });

       $.get("/lineups", function(data) {

                $("#lineups").html(data);

                var lineupsTable = $("#channelLineupsTable");
                
                $("#channelLineupsTable").DataTable({
                    'paging': false
                });


                tableEdit($("#channelLineupsTable"));


                $('#addLineup').click(function() {

                    $("#addLineupModal").modal('show');

                    $("#submitZipcode").click(function() {
                        console.log('submit')
                    })
                });


                $('#addStation').click(function() {

                    console.log('add_station')

                    $("#addStationModal").modal('show');

                    $("#submitStation").click(function() {

                        console.log('click submit add station')

                           console.log($("#addStationForm").serialize())

                       $.post('/addStation',$("#addStationForm").serialize(),function(data){

                            console.log(data)
                        });
                        
                    })
                });
    });

        $.get("/docs", function(data) {
        $("#docs").html(data);
    });
/**************************************************************************************/
// var lineupedits = [];

    function tableEdit(table) {

        let origValue;
        let edits = [];

        cell = table.find('td');
        checkbox = table.find('input[type="checkbox"]')

        $("#save_lineups").on('click', function() {
            save();
        })

        let save = function() {
            console.log(edits)

            params = {
                "edits": edits
            }

            $.post('/lineups', params, function(data) {

                edits = [];

            })
        }

        cell.on('click', function() {
            if ($(this).attr("contentEditable")) {
                origValue = $(this).text();
            }
        })

        checkbox.on('change', function() {



            let checkbox;
            let id = $(this).parent().parent().attr('id')
            let col = $(this).attr('name')
            console.log(col)

            console.log(id, col)

            if ($(this).is(":checked")) {
                checkbox = 1;
                row = {
                    id: id,
                    col: col,
                    value: checkbox
                }
                edits.push(JSON.stringify(row))

                console.log('checked')
            } else {
                checkbox = 0;
                row = {
                    id: id,
                    col: col,
                    value: checkbox
                }
                edits.push(JSON.stringify(row))
                console.log('not checked')
            }

        })

        cell.on('blur', function() {

            let value = $(this).text();
            let id = $(this).parent().attr('id')
            let col = $(this).attr('class')

            row = {
                id: id,
                col: col,
                value: value.trim()
            }

            if (value === origValue) {
                console.log(value + ' has not changed')
            } else {
                edits.push(JSON.stringify(row));
                console.log(row)
            }

        })
    }



 
 /**************************************************************************************/
   



});








