
def tables():

    import mysql_utils1
    connection = mysql_utils1.connect_to_mysql()
    cursor = connection.cursor()

    try:
        cursor.execute("SHOW TABLES LIKE 'collaborator_path'")
        table_exists = cursor.fetchone()

        # If collaborator_path table does not exist, create it
        if not table_exists:
            create_table_query = """
        CREATE TABLE `academicworld`.`collaborator_path` (
                      `faculty1_id` INT NOT NULL,
                      `faculty2_id` INT NOT NULL,
                      `Path` VARCHAR(512) NULL,
                      INDEX `id_idx2` (`faculty2_id` ASC) INVISIBLE,
                      PRIMARY KEY (`faculty1_id`, `faculty2_id`),
                      INDEX `id_idx1` (`faculty1_id` ASC) VISIBLE,
                      CONSTRAINT `f_id1`
                        FOREIGN KEY (`faculty1_id`)
                        REFERENCES `academicworld`.`faculty` (`id`)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,
                      CONSTRAINT `f_id2`
                        FOREIGN KEY (`faculty2_id`)
                        REFERENCES `academicworld`.`faculty` (`id`)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE);  
        )
        """
            cursor.execute(create_table_query)
        else:
            cursor.execute("TRUNCATE TABLE collaborator_path;")
            print("collaborator_path table already exists...")
    except:
        pass

    cursor.execute("SHOW TABLES LIKE 'collaborator_path'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("SHOW TRIGGERS LIKE 'before_insert_check_duplicates'")

        bicd_trigger_exists = cursor.fetchall()
        print(bicd_trigger_exists)
        if bicd_trigger_exists == None:
            print('here')
            cursor.execute("""
                    CREATE TRIGGER before_insert_check_duplicates
                    BEFORE INSERT ON `collaborator_path`
                    FOR EACH ROW
                    BEGIN
                        DECLARE duplicate_count INT;

                        SELECT COUNT(*) INTO duplicate_count
                        FROM collaborator_path
                        WHERE (faculty1_id = NEW.faculty1_id AND faculty2_id = NEW.faculty2_id)
                           OR (faculty1_id = NEW.faculty2_id AND faculty2_id = NEW.faculty1_id);

                        IF duplicate_count > 0 THEN
                            SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'Error: Faculty1 and Faculty2 already in table';
                        END IF;
                    END;
                """)
        else:
            print("before_insert_check_duplicates exists")
        cursor.execute(
            "SHOW TRIGGERS LIKE 'before_insert_check_faculty_existence'")
        bicfe_trigger_exists = cursor.fetchall()
        print(bicfe_trigger_exists)
        if bicd_trigger_exists == None:
            print('here')
            cursor.execute("""
                    CREATE  TRIGGER before_insert_check_faculty_existence
                    BEFORE INSERT ON `collaborator_path`
                    FOR EACH ROW
                    BEGIN
                        DECLARE faculty1_exists INT;
                        DECLARE faculty2_exists INT;

                        SELECT COUNT(*) INTO faculty1_exists
                        FROM faculty
                        WHERE id = NEW.faculty1_id;

                        SELECT COUNT(*) INTO faculty2_exists
                        FROM faculty
                        WHERE id = NEW.faculty2_id;

                        IF faculty1_exists = 0 OR faculty2_exists = 0 THEN
                            SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'Error: Faculty1 and Faculty2 do not exist';
                        END IF;
                    END;
                """)
        else:
            print("before_insert_check_faculty_existence exists")
        cursor.execute(
            "SHOW TRIGGERS LIKE 'prevent_same_faculty_insert'")
        psfe_trigger_exists = cursor.fetchall()
        print(psfe_trigger_exists)
        if psfe_trigger_exists == None:
            print('here')
            cursor.execute("""
                    CREATE  TRIGGER prevent_same_faculty_insert
                    BEFORE INSERT ON `collaborator_path`
                    FOR EACH ROW
                    IF NEW.faculty1_id = NEW.faculty2_id THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Error: Faculty1 and Faculty2 cannot be the same';
                    END IF
                    END;
                """)
        else:
            print("prevent_same_faculty_insert exists")
        view_creator = "CREATE VIEW university_names AS SELECT name FROM university;"
        view_checker = "SELECT COUNT(*) AS view_exists FROM information_schema.views " \
            "WHERE table_schema = %s AND table_name = %s"
        connection = mysql_utils1.connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                view_checker, ('academicworld',  'university_names'))
            result = cursor.fetchall()
            if result is not None and result[0][0] > 0:
                print("The university_names view exists.")
            else:
                cursor.execute(view_creator)
