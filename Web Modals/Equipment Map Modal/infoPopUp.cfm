<CFOUTPUT>
    <cfset propID=#url.id#>
</cfoutput>

<cfscript>
    // CREATE OBJECT
    query = createObject("component", "#application.eqcfc#");
    // CALL THE FUNCTION
    myReturn = query.getAllEquips(propID, false);
</cfscript>
<cfset return_table=myReturn>
<!--- <cfdump var="#return_table#"> --->
<head>
    <link rel="stylesheet" type="text/css" href="css/bootstrap.min.css"/>
    <link rel="stylesheet" type="text/css" href="css/font-awesome-4.7.0/css/font-awesome.min.css"/>
    <link rel="stylesheet" type="text/css" href="css/libs/nanoscroller.css"/>
    <link href='//fonts.googleapis.com/css?family=Open+Sans:400,600,700,300|Titillium+Web:200,300,400' rel='stylesheet' type='text/css'>

    <link rel="stylesheet" type="text/css" href="css/theme_styles.css"/>
</head>
<body>
    <style media="screen">
        #equipHead {
            background: #80b4d3;
            color: white;
        }
        a{
            color: #80b4d3;
        }
        .content {
            background: #E6E6E6;
        }
        #equipTable {
            border-collapse: collapse;

        }
        table,
        td,
        th {
            border: 1px solid white;
        }

    </style>
    <div class="col-lg-12" style="padding:10px;">
        <cfoutput>
            <h1 align="center" style="color:gray;">
                Equipment Information for #myReturn.address#
            </h1>
        </cfoutput>

        <table align="center" class="table table-bordered" id="equipTable">
            <tbody >
                <!--- <th>
              Address</th> --->
                <tr id="equipHead">
                    <th>
                        Contractor</th>
                    <th>
                        Equipment Name</th>
                    <th>
                        Equipment Type</th>
                    <th>
                        Operator</th>
                    <th>
                        Equipment Check Out Time
                    </th>

                    <th>
                        Condition
                    </th>
                </tr>

                <cfoutput query="return_table">

                    <tr class="content" align="center">
                        <!--- <td>#trim(address)#</td> --->
                        <td>#trim(companyname)#</td>
                        <td>#trim(EQ_EQDESC)#</td>
                        <td>#trim(EQ_TYPEDESC)#</td>
                        <td >
                          <cfset mailtolink = "mailto:" & "#trim(EQ_email)#" & "?Subject=Regarding%20Equipment%20Item:%20" & "#reReplace(trim(EQ_EQDESC), "[ ,-]+", "%20", "all")#" />
                          <a href="#mailtolink#" target="_top">#trim(EQ_OPERATOR)#</a>
                        </td>
                        <td>#trim(EQ_checkouttime)#</td>

                        <td>#trim(EQ_CONDITON)#</td>

                    </tr>

                </cfoutput>
            </tbody>
        </table>
    </div>

</body>
