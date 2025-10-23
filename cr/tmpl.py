def get_credit_header(lang_name, comment_style):
    developer = "mero"
    telegram = "qp4rm"
    tool_name = "CodeAlchemist"
    
    if comment_style == "#":
        return f"""# ========================================
# Tool: {tool_name}
# Developer: {developer}
# Telegram: @{telegram}
# ========================================

"""
    elif comment_style == "//":
        return f"""// ========================================
// Tool: {tool_name}
// Developer: {developer}
// Telegram: @{telegram}
// ========================================

"""
    elif comment_style == "--":
        return f"""-- ========================================
-- Tool: {tool_name}
-- Developer: {developer}
-- Telegram: @{telegram}
-- ========================================

"""
    elif comment_style == "%":
        return f"""% ========================================
% Tool: {tool_name}
% Developer: {developer}
% Telegram: @{telegram}
% ========================================

"""
    elif comment_style == ";":
        return f"""; ========================================
; Tool: {tool_name}
; Developer: {developer}
; Telegram: @{telegram}
; ========================================

"""
    elif comment_style == "'":
        return f"""' ========================================
' Tool: {tool_name}
' Developer: {developer}
' Telegram: @{telegram}
' ========================================

"""
    elif comment_style == "*":
        return f"""* ========================================
* Tool: {tool_name}
* Developer: {developer}
* Telegram: @{telegram}
* ========================================

"""
    elif comment_style == "REM":
        return f"""REM ========================================
REM Tool: {tool_name}
REM Developer: {developer}
REM Telegram: @{telegram}
REM ========================================

"""
    elif comment_style == "!":
        return f"""! ========================================
! Tool: {tool_name}
! Developer: {developer}
! Telegram: @{telegram}
! ========================================

"""
    else:
        return f"""/*
 * ========================================
 * Tool: {tool_name}
 * Developer: {developer}
 * Telegram: @{telegram}
 * ========================================
 */

"""

def get_readme_credits():
    return """========================================
CodeAlchemist
========================================
Developer: mero
Telegram: @qp4rm
========================================
This archive was created using CodeAlchemist
A powerful code translation and compression tool
========================================
"""
