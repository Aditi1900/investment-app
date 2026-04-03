================================================================
         PROGRAM DOCUMENTATION GUIDELINES
================================================================

Fields marked "if N/A - None" must still appear with the literal
value None so readers know the field was considered.

  ----------------------------------------------------------------
  CLASSES
  ----------------------------------------------------------------

  # PURPOSE:
  #    -<ClassName> provides <X> abstraction
  #    -<why the abstraction exists>

  ----------------------------------------------------------------
  FUNCTIONS
  ----------------------------------------------------------------

  # INPUT: if N/A - None
  #    -<param_name>(type); <what it represents>
  # OUTPUT: if N/A - None
  #    -<var_name>(type); <what it represents>
  # PRECONDITION: if N/A - None
  #    -<param_name or state>; <value constraint>
  # POSTCONDITION: if N/A - None
  #    -<param or state>; <observable guarantee after return>
  # RAISES: if N/A - None
  #    -<ExceptionType>; <condition that triggers it>
  def function_name(param_name: type) -> type:
      return var_name

  ----------------------------------------------------------------
  STYLE RULES
  ----------------------------------------------------------------

  Semicolons    Separate name/type from description with "; "

  Indentation   Labels flush-left one space; entries indented with TAB

  Types         Use Python builtins or typing module. Project-defined
                types are listed in the TYPES section below. Persistent
                types carry id (database primary key). Nested collections
                may be abbreviated in higher layers when element types are
                defined in a referenced POSTCONDITION.

  Constraints   State value constraints, not types
                ("n > 0" not "must be int")

  Guarantees    Describe observable state, not implementation details

  Be brief      Short phrase per entry, not full sentences


================================================================
         PROGRAM MODELS
================================================================

  ----------------------------------------------------------------
  TYPES
  ----------------------------------------------------------------

  User         Represents a user account; holds login, balance and collection of portfolios
  Portfolio    Represents named collection of stocks
  Stock        Represents a stock holding; ticker and quantity

  ----------------------------------------------------------------
  DATA MODELS
  ----------------------------------------------------------------

  JSON response bodies returned by the Frontend API.

  PortfolioData
  {
      "name": "tech",
      "stocks": {
          "AAPL": {
              "ticker": "AAPL",
              "quantity": 10
          }
      }
  }

  UserData
  {
      "login": "john_doe",
      "balance": 1000.00,
      "portfolios": {
          "tech": { ... }  // see PortfolioData
      }
  }