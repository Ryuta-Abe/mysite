var db = new Mongo().getDB( "sensordb" );
var col = db.getCollection( "sensor2" );
var data = col.find().sort( { device_id:40add53c } );
print( "User Agent Summary \n" );
data.forEach( function( data ) { print( "Agent = " + data.device_id ); } );