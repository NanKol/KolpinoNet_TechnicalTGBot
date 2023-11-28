function getobjectname($conn, $objid) {
        if (intval ( $objid ) > 0) {
                $sql = "SELECT * FROM objects WHERE id=$objid LIMIT 1";
                $allobjects = mysqli_query ($conn, $sql ) or myerr ();
                if (mysqli_num_rows ( $allobjects ) > 0) {
                        $curobj = mysqli_fetch_array ( $allobjects );

                        $fulladdr = getstreet ($conn, $curobj ['street'] ) . " . $curobj ['dom'];
                        if (strlen ( $curobj ['korp'] ) > 0)
                                $fulladdr .= " . $curobj ['korp'];
                        ;
                        return $fulladdr;
                }
                ;
        }
}

function getstreet($conn, $streetid) {
        if (intval ( $streetid ) > 0) {
                $sql = "SELECT ost.streettype, os.street,oc.name as cityname FROM objects_streets as os
         LEFT JOIN objects_streets_types as ost ON (os.streettype=ost.id)
         LEFT JOIN objects_city as oc ON (oc.id=os.city)
         WHERE os.id=$streetid";
                $result = mysqli_query ($conn, $sql ) or myerr ();
                if (mysqli_num_rows ( $result ) > 0) {
                        $currstreet = mysqli_fetch_assoc ( $result );
                        $strname = $currstreet ['cityname'] . ", " . $currstreet ['street'];
                        if (strlen ( $currstreet ['streettype'] ) > 0)
                                $strname .= " " . $currstreet ['streettype'];
                        return $strname;
                }
        }
}