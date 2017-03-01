CREATE DEFINER=`tfuser`@`%` PROCEDURE `updateTom`(in temp1 VARCHAR(30) )
BEGIN
    DECLARE tabname VARCHAR(30);
    set tabname = temp1;
    set @minid = 0;
    set @maxid = 0;
    set @findFClose = 0.0;
    SET @STMT :=CONCAT("select id into @minid from `",tabname,"` where id=(select min(id) from `",tabname,"`);");   
    PREPARE STMT FROM @STMT;   
    EXECUTE STMT;
    SET @STMT :=CONCAT("select id into @maxid from `",tabname,"` where id=(select max(id) from `",tabname,"`);");   
    PREPARE STMT FROM @STMT;   
    EXECUTE STMT;
    -- select id into minid from text where id=(select min(id) from text);
    -- select id into maxid from text where id=(select max(id) from text);
    
    WHILE @minid < @maxid DO   
        SET @STMT :=CONCAT("SELECT close into @findFClose from `",tabname,"` where id=@minid+1;");   
        PREPARE STMT FROM @STMT;   
        EXECUTE STMT;
        SET @STMT :=CONCAT("update `",tabname,"` set tomorrow=@findFClose where id=@minid; ");   
        PREPARE STMT FROM @STMT;   
        EXECUTE STMT;
        -- SELECT fclose into findFClose from shares_dat.text where id=(minid+1);
        -- update text set tomorrow=findFClose where id=minid; 
        SET @minid = @minid+1;   
    END WHILE; 
END