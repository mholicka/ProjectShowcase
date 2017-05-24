<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Contractor Filter</title>
	<!--- <script src="https://code.jquery.com/jquery-3.1.1.min.js"></script> --->
	<!--- <link href="css/bootstrap.min.css" rel="stylesheet"> --->
	<link href="contractFilter/css/main.css" rel="stylesheet">
	<script type="text/javascript" src="contractFilter/js/standalone/selectize.js"></script>
	<script type="text/javascript" src="contractFilter/js/main.js"></script>
	<link rel="stylesheet" href="contractFilter/css/selectize.bootstrap3.css">
</head>
<body>
	<CFOUTPUT>
		<INPUT NAME="tableID" TYPE="hidden" id="tableID" VALUE="#tableType#">
	</CFOUTPUT>

	<div class="container" style="min-width:100%">

		<div align="center" class="form-wrapper">
			<cfif tableType LT 3>
				<p>


					Please select from the filters below OR backspace and then type into the filters and select from the drop-down options.</p>
				<div class="form-inline ">
					<div class="form-group">
						<cfoutput>
							<select class="form-control selectized" placeholder="Select a Company" name="cName" id='cName'>
								<option value=-1 selected hidden>
									All Vendor Names</option>
								<cfloop query="contractors">
									<option value="#contractors.id#">
										#trim(contractors.CompanyName)#</option>
								</cfloop>
							</select>

							<select class="form-control selectized" placeholder="Select a Trade" name="trd" id='trd'>
								<option value=-1 selected hidden>
									All Trades</option>
								<cfloop query="trades">
									<option value="#trades.id#">
										#trim(trades.english)#</option>
								</cfloop>
							</select>
							<select class="form-control selectized" placeholder="Select a City" name="city" id='city'>
								<option value=-1 selected hidden>
									All Cities</option>
								<cfloop query="locs">
									<option value="#locs.city#">
										#trim(locs.city)#</option>
								</cfloop>
							</select>
							<select class="form-control selectized" placeholder="Select a Region" name="loc" id='loc'>
								<option value=-1 selected hidden>
									All Provinces</option>
								<cfloop query="locs">
									<option value="#locs.province#">
										#trim(locs.province)#</option>
								</cfloop>
							</select>

						</cfoutput>
					</div>
				</div>
			<cfelse>
				<select class="form-control selectized" placeholder="Select a Company" name="cName" id='cName' style="display:none;">
					<option value=-1 selected hidden>
						Select a Company</option>
				</select>
				<select class="form-control selectized" placeholder="Select a Trade" name="trd" id='trd' style="display:none;">
					<option value=-1 selected hidden>
						Select a Trade</option>
				</select>
				<select class="form-control selectized" placeholder="Select a Region" name="loc" id='loc' style="display:none;">
					<option value=-1 selected hidden>
						Select a Province</option>
				</select>
			</cfif>
		</div>

		<div class="table-responsive ">
			<table id="contractTable" class="table contractorTable table-hover table-bordered ">
				<tbody>
					<!--- <tr></tr> --->
				</tbody>
			</table>
		</div>
		<div class="text-center" style="padding-bottom: 10px;">
			<cfif tableType LT 3>
				<button type="button" name="button" class="btn btn-success" onclick="updatevendors()">
					Submit All
				</button>
			</cfif>
		</div>

	</div>
</body>
</html>
