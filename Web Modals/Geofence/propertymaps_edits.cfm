
<cfparam name="session.masteraccess" default="0">
<!DOCTYPE html>

<html lang="en">

	<head>

		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<meta name="description" content="">
		<meta name="author" content="">
		<title>Geolocation- Admin View</title>
		<!-- Bootstrap Core CSS -->
		<link href="css/bootstrap.min.css" rel="stylesheet">
		<link href="css/geolocation.css" rel="stylesheet">
		<!-- Custom CSS -->
		<link href="css/simple-sidebar.css" rel="stylesheet">
		<!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
		<!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
		<!--[if lt IE 9]> <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script> <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script> <![endif]-->
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		</head>

	<body>
		<CFOUTPUT>
			<cfset buildID=#url.id#>
			<cfset outline=#url.outline#>
			<INPUT NAME="propID" TYPE="hidden" id="propID" VALUE="#buildID#">
			<INPUT NAME="type" TYPE="hidden" id="mapType" VALUE="#outline#">
		</CFOUTPUT>
		<div id="wrapper">

			<!-- Sidebar -->
			<div class="col-xs-2" id="instruction_table">
				<!--- <cfif outline is "so"> --->
					<div id="sidebar-wrapper" class="hovering">
					<!--- <cfelse>
						<div id="sidebar-wrapper" class="hovering"> --->
						<!--- </cfif> --->

						<!--- <div id="sidebar-wrapper" class="fading"> --->
						<!--- <div class="fill"> --->
						<!--- <div class="table-responsive " style="text-align:center">

						</div> --->

						<!---
                        <span style="padding-left:8.5%; padding-right:3px; padding-top:2%; padding-bottom:2%; display:block;">
                        	<img style="width:30%;vertical-align:bottom" id="company" align="middle"  alt="">
                            <img id="crawford_compliance" style="margin-left:10%;width:30%;" align="middle"  alt=""></span>
 --->

						<!--- src="../logos/powered-by-cc-padded.png "src="../logos/colliers-snowtracker-02.jpg" --->

						<table id="pickTable" class="table partialfill">
							<tr>
								<td colspan="2" align="center" style="padding-top:5%;padding-bottom:5%">

									<cfif session.masteraccess is 8>
										<img src="../logos/crawford-logo.png" style="width:50%;image-rendering: -moz-crisp-edges;">
									</cfif>
									<cfif session.masteraccess is 0>
										<img src="../logos/cc-logo.png" style="width:50%;image-rendering: -moz-crisp-edges;">
									</cfif>
									<cfif session.masteraccess is 7>
										<img src="../logos/colliers-logo.png" style="width:50%;image-rendering: -moz-crisp-edges;">
									</cfif>
								</td>
							</tr>
							<tr>
								<td colspan="2" class="sitemap_ctrl sitemap_ui" align="center">
									<span style="display:block;margin:auto;padding-right:2%;padding-left:0%" class="basic-grey">
									<input type="button" class="btn btn-submit btn-space " class="instrbut" value="POLYGON MODE" onclick="re_init()" style=" padding:5px  5px 5px 5px;">
									<input type="button" class="btn btn-submit btn-space" style="padding:5px 5px 5px 5px;" class="instrbut" value="ROUTING MODE" onclick="routingMode(false)">
								</span>
								</td>

							</tr>
							<tr>
								<td colspan="3" style="padding-left: 2%;font-size: large ;font-weight: bold;">To create your designated areas:</td>
								<!--- <br/> --->

								<!--- <INPUT TYPE="submit" VALUE="Get Property Polygons" onClick="postGeoJSON()"></td> --->
							</tr>

							<tr>
								<td class="numbers">Step 1</td>
								<!--- <td>Starting Out</td> --->
								<td colspan="2" class="instr" id="s1">Select the polygon tool
									<img src="img/Misc/poly_shape.png" alt="Polygon make">
									at the bottom of the map</td>
							</tr>
							<tr>
								<td class="numbers">Step 2</td>
								<td class="instr" id="ui_instr">Create a polygon by clicking on the map around the area you would like to designate.</td>

							</tr>
							<cfif outline is "so">
								<tr id="example">
									<td colspan="2"><img src="img/Misc/example_siteoutline.png" alt="Example Site Outline"></td>
								</tr>
							</cfif>

							<!--- this really should be dynamic based on the control panel, but not enough time..  --->
							<tr class="sitemap_ui">
								<td class="numbers">Step 3</td>
								<td colspan="2" class="instr">
									Choose an area type
									<br/>
									<select id="polytype" class="basic-grey">
										<option value="General Area" selected="selected">
											General Area</option>
										<option value="Dump Location">
											Dump Location</option>
										<option value="No Snow Dumping">
											No Snow Dumping</option>
										<option value="Priority Area">
											Priority Area</option>
									</select>
								</td>
							</tr>
							<tr>

							</tr>
							<tr class="sitemap_ui">
								<td class="numbers">Step 4</td>
								<!--- <td>Area Name</td> --->
								<td colspan="2" class="instr">
									<span>Name the Area</span><br/>
									<input class=basic-grey id="areaName" type="text" name="Area_Label" value="test" font-family: "Arial" font-size: 1em ;>
								</td>
							</tr>
							<tr class="sitemap_ui">
								<td  class="numbers">Step 5</td>
								<td colspan="2" class="instr">
									<p>When finished,click confirm polygon.<br/></p><input type="button" class="btn btn-submit btn-space" value="CONFIRM POLYGON" onclick=makeMarker() style="padding: 5px 5px 5px 5px;" id="confirm">
								</tr>
								<tr class="sitemap_ctrl sitemap_ui">
									<td class="numbers" id ="s6">Step 6</td>
									<td colspan="2" class="instr">
										<p>Optional:To delete a polygon, click on the polygon you want to change, which will turn it red, then click on "delete polygon" below<br/></p>
										<!--- background:#666666 --->
										<span style="padding-right:2%;padding-left:0%" class="basic-grey">
											<input id="del" type="button" class="btn btn-submit btn-space sitemap_ctrl " value="DELETE POLYGON" onclick=clearMap("") style=" padding:5px  5px 5px 5px;">
											<input id="delAll" type="button" class="btn btn-submit btn-space " style="padding:5px 5px 5px 5px;" class="instrbut" value="CLEAR ALL POLYGONS" onclick=clearMap("all")>
											<!--- <input type="button" class="basic-grey" style="padding:5px 5px 5px 5px;background: #666666;color:white;" class="instrbut" value="Getpolygons" onclick=postGeoJSON()> --->
										</span>
									</td>

								</tr>
								<tr class="sitemap_ui">
									<td class="numbers">Step 7</td>
									<td colspan="2" class="instr">
										<p>Optional:To edit the polygons use the hand tool
											<img src="img/Misc/poly_hand.png" alt="Polygon select">
											at the bottom of the map, then grab the white edges and drag to the desired location.<br/></p>
										<!--- background:#666666 --->

									</tr>

									<tr>
										<td colspan="3" style="margin:auto;padding-left: 2%;font-size: medium;font-weight: bold; padding-right:2%;padding-bottom:1%;">
											<p id="final_text">Repeat steps 1 - 6 until you have created all of your designated areas,routes and POIs. Once you are finished, click the submit button below.&nbsp;</p>

											<input type="button" class="btn btn-primary" value="SUBMIT OVERLAY" onclick=generateJSON("sitemap",false) id="final_submit" style="display:block;margin:auto;font-size:large;">
											<br>
											<input type="button" class="btn btn-submit btn-space" id="skipButton" value="SKIP" onclick="window.close()" style="margin:auto; display:block">
											<!--- style="display:block;margin:auto;background:#248bca;color:white;width:95%;font-size:large" --->
										</td>
									</tr>

									<!--- <td >
      							<div id="out"></div>
      						</td> --->
								</table>

							</div>
						</div>
						<!-- /#sidebar-wrapper -->

						<!-- Page Content -->

						<div class=" col-xs-10 ">
							<div id="map"></div>
							<div class="row-fluid">
								<div id="legend" style="display:none">
									<h4 style="text-align:center;">Area Types</h4>
								</div>
							</div>

						</div>

					</div>
				</div>

				<!-- /#wrapper -->

				<!-- jQuery -->
				<script src="js/jquery.js"></script>

				<!-- Bootstrap Core JavaScript -->
				<script src="js/bootstrap.min.js"></script>

				<!-- Menu Toggle Script -->

				<script>
					var assID = <cfoutput>#session.masterAccess#</cfoutput>
					// var assID= 7;
				</script>

				<script sync src="js/refractored/globalvars.js"></script>
				<script sync type="text/javascript" src="js/refractored/main_map.js"></script>
				<script sync type="text/javascript" src="js/refractored/posting_geoJSON.js"></script>
				<script sync type="text/javascript" src="js/refractored/making_geoJSON.js"></script>
				<script sync type="text/javascript" src="js/refractored/routing.js"></script>
				<script sync type="text/javascript" src="js/refractored/drawing.js"></script>
				<script sync type="text/javascript" src="js/refractored/siteoutline.js"></script>


			</body>

		</html>
