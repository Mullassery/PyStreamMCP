# Security Vulnerability Audit - PyStreamMCP

**Audit Date:** 2026-10-27
**Repository:** /Users/georgimullassery/Desktop/Projects/PyStreamMCP
**Total Findings:** 947

## Summary
- **Critical:** 798
- **High:** 25
- **Medium:** 124

## Findings

### 1. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/Image.py:3791
- **Description:** eval()
- **Evidence (Line):** `def eval(image: Image, *args: Callable[[int], float]) -> Image:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 2. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/PIL/ImageFont.py:1272
- **Description:** AWS Access Key detected
- **Evidence (Line):** `QAHAEwAAQAAAAAAAgAHAGQAAQAAAAAAAwAaAKIAAQAAAAAABAAHAM0AAQAAAAAABQA8AU8AAQAAAA`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 3. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/ImageMath.py:239
- **Description:** eval()
- **Evidence (Line):** `def lambda_eval(expression: Callable[[dict[str, Any]], Any], **kw: Any) -> Any:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 4. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/ImageMath.py:267
- **Description:** eval()
- **Evidence (Line):** `def unsafe_eval(expression: str, **kw: Any) -> Any:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 5. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/ImageMath.py:269
- **Description:** eval()
- **Evidence (Line):** `Evaluates an image expression. This uses Python's ``eval()`` function to process`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 6. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/ImageMath.py:310
- **Description:** eval()
- **Evidence (Line):** `out = builtins.eval(expression, None, args)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 7. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/ImageShow.py:125
- **Description:** os.system()
- **Evidence (Line):** `os.system(self.get_command(path, **options))  # nosec`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 8. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/_code/code.py:164
- **Description:** eval()
- **Evidence (Line):** `def eval(self, code, **vars):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 9. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/_code/code.py:173
- **Description:** eval()
- **Evidence (Line):** `return eval(code, self.f_globals, f_locals)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 10. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/_code/code.py:326
- **Description:** eval()
- **Evidence (Line):** `# however via `exec(...)` / `eval(...)` they can be other types`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 11. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/_code/code.py:326
- **Description:** exec()
- **Evidence (Line):** `# however via `exec(...)` / `eval(...)` they can be other types`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 12. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/_py/path.py:1153
- **Description:** exec()
- **Evidence (Line):** `exec(f.read(), mod.__dict__)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 13. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/_py/path.py:1159
- **Description:** exec()
- **Evidence (Line):** `def sysexec(self, *argv: os.PathLike[str], **popen_opts: Any) -> str:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 14. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:188
- **Description:** exec()
- **Evidence (Line):** `exec(co, module.__dict__)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 15. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:393
- **Description:** marshal load
- **Evidence (Line):** `co = marshal.load(fp)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 16. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/capture.py:1112
- **Description:** os.system()
- **Evidence (Line):** `os.system('echo "hello"')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 17. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/capture.py:1140
- **Description:** os.system()
- **Evidence (Line):** `os.system('echo "hello"')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 18. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/mark/__init__.py:66
- **Description:** eval()
- **Evidence (Line):** `def test_eval(test_input, expected):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 19. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/mark/__init__.py:67
- **Description:** eval()
- **Evidence (Line):** `assert eval(test_input) == expected`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 20. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/mark/expression.py:295
- **Description:** eval()
- **Evidence (Line):** `"""Adapts a matcher function to a locals mapping as required by eval()."""`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 21. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/mark/expression.py:353
- **Description:** eval()
- **Evidence (Line):** `return bool(eval(self._code, {"__builtins__": {}}, MatcherAdapter(matcher)))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 22. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/pytester.py:296
- **Description:** eval()
- **Evidence (Line):** `if eval(check, backlocals, call.__dict__):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 23. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/skipping.py:92
- **Description:** eval()
- **Evidence (Line):** `If an old-style string condition is given, it is eval()'d, otherwise the`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 24. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/_pytest/skipping.py:119
- **Description:** eval()
- **Evidence (Line):** `result = eval(condition_code, globals_)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 25. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/anyio/_backends/_asyncio.py:2796
- **Description:** exec()
- **Evidence (Line):** `# Use loop.subprocess_shell()/subprocess_exec() rather than their`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 26. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/anyio/_backends/_asyncio.py:2810
- **Description:** exec()
- **Evidence (Line):** `transport, protocol = await loop.subprocess_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 27. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/anyio/to_interpreter.py:123
- **Description:** exec()
- **Evidence (Line):** `exc_info = _interpreters.exec(self._interpreter_id, _run_func)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 28. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/anyio/to_interpreter.py:130
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.loads(res)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 29. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/anyio/to_process.py:95
- **Description:** pickle load/dumps
- **Evidence (Line):** `retval = pickle.loads(pickled_response)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 30. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/anyio/to_process.py:220
- **Description:** pickle load/dumps
- **Evidence (Line):** `command, *args = pickle.load(stdin.buffer)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 31. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/attr/_make.py:216
- **Description:** eval()
- **Evidence (Line):** `def _compile_and_eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 32. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/attr/_make.py:227
- **Description:** eval()
- **Evidence (Line):** `eval(bytecode, globs, locs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 33. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/attr/_make.py:260
- **Description:** eval()
- **Evidence (Line):** `_compile_and_eval(script, globs, locs, filename)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 34. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/attr/_make.py:1690
- **Description:** eval()
- **Evidence (Line):** `_compile_and_eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 35. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/attr/_make.py:1810
- **Description:** eval()
- **Evidence (Line):** `_compile_and_eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 36. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/attr/_make.py:1884
- **Description:** eval()
- **Evidence (Line):** `_compile_and_eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 37. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/ai/agents/_utils/serialization.py:830
- **Description:** eval()
- **Evidence (Line):** `return eval(data_type)(data)  # nosec # pylint: disable=eval-used`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 38. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/ai/agents/_utils/serialization.py:1786
- **Description:** eval()
- **Evidence (Line):** `return eval(data_type)(attr)  # nosec # pylint: disable=eval-used`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 39. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/ai/agents/aio/operations/_patch.py:1314
- **Description:** eval()
- **Evidence (Line):** `response_json = ast.literal_eval(str(response))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 40. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/ai/agents/operations/_patch.py:1321
- **Description:** eval()
- **Evidence (Line):** `response_json = ast.literal_eval(str(response))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 41. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/azure/identity/_constants.py:50
- **Description:** Password Assignment detected
- **Evidence (Line):** `AZURE_CLIENT_CERTIFICATE_PASSWORD = "AZURE_CLIENT_CERTIFICATE_PASSWORD"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 42. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/azure/identity/_constants.py:55
- **Description:** Password Assignment detected
- **Evidence (Line):** `AZURE_PASSWORD = "AZURE_PASSWORD"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 43. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/identity/aio/_credentials/azd_cli.py:215
- **Description:** exec()
- **Evidence (Line):** `proc = await asyncio.create_subprocess_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 44. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/identity/aio/_credentials/azure_cli.py:220
- **Description:** exec()
- **Evidence (Line):** `proc = await asyncio.create_subprocess_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 45. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/azure/identity/aio/_credentials/azure_powershell.py:190
- **Description:** exec()
- **Evidence (Line):** `proc = await asyncio.create_subprocess_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 46. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/cffi/_cffi_gen_src.py:53
- **Description:** exec()
- **Evidence (Line):** `exec(compiled, globs, globs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 47. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/cffi/recompiler.py:80
- **Description:** eval()
- **Evidence (Line):** `flags = eval(self.flags, G_FLAGS)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 48. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/cffi/setuptools_ext.py:26
- **Description:** exec()
- **Evidence (Line):** `exec(code, glob, glob)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 49. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/coverage/execfile.py:222
- **Description:** exec()
- **Evidence (Line):** `exec(code, main_mod.__dict__)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 50. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/coverage/execfile.py:335
- **Description:** marshal load
- **Evidence (Line):** `code = marshal.load(fpyc)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 51. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/coverage/htmlfiles/coverage_html.js:236
- **Description:** exec()
- **Evidence (Line):** `const match = /\.([0-9]+)/.exec(cell.textContent);`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 52. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/coverage/parser.py:691
- **Description:** eval()
- **Evidence (Line):** `return True, eval(node.id)  # pylint: disable=eval-used`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 53. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/coverage/templite.py:70
- **Description:** exec()
- **Evidence (Line):** `exec(python_source, global_namespace)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 54. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/_oid.py:372
- **Description:** Password Assignment detected
- **Evidence (Line):** `AttributeOID.CHALLENGE_PASSWORD: "challengePassword",`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 55. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/primitives/serialization/ssh.py:77
- **Description:** Private Key detected
- **Evidence (Line):** `_SK_START = b"-----BEGIN OPENSSH PRIVATE KEY-----"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 56. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/dirtyjson/loader.py:202
- **Description:** eval()
- **Evidence (Line):** `res = eval(m.string[m.pos:m.end()])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 57. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/dirtyjson/tests/test_decode.py:29
- **Description:** eval()
- **Evidence (Line):** `self.assertEqual(dirtyjson.loads(s), eval(s))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 58. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/dirtyjson/tests/test_decode.py:31
- **Description:** eval()
- **Evidence (Line):** `self.assertEqual(dirtyjson.loads(s), eval(s))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 59. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/dirtyjson/tests/test_decode.py:33
- **Description:** eval()
- **Evidence (Line):** `self.assertEqual(dirtyjson.loads(s), eval(s))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 60. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/flask/cli.py:150
- **Description:** eval()
- **Evidence (Line):** `args = [ast.literal_eval(arg) for arg in expr.args]`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 61. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/flask/cli.py:152
- **Description:** eval()
- **Evidence (Line):** `kw.arg: ast.literal_eval(kw.value)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 62. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/flask/cli.py:1031
- **Description:** eval()
- **Evidence (Line):** `eval(compile(f.read(), startup, "exec"), ctx)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 63. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/flask/config.py:209
- **Description:** exec()
- **Evidence (Line):** `exec(compile(config_file.read(), filename, "exec"), d.__dict__)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 64. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/frontmatter/default_handlers.py:260
- **Description:** yaml.load (unsafe)
- **Evidence (Line):** `return yaml.load(fm, **kwargs)  # type: ignore[arg-type]`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 65. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/gui.py:312
- **Description:** eval()
- **Evidence (Line):** `return ast.literal_eval(self.kwargs.value) or {}`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 66. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/spec.py:1718
- **Description:** Password Assignment detected
- **Evidence (Line):** `>>> fs = filesystem('ftp', host='test.rebex.net', user='demo', password='password')`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 67. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/tests/abstract/mv.py:36
- **Description:** os.system()
- **Evidence (Line):** `os.system(f'icacls "{protected_path}" /deny Everyone:(W)')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 68. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/tests/abstract/mv.py:55
- **Description:** os.system()
- **Evidence (Line):** `os.system(f'icacls "{protected_path}" /remove:d Everyone')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 69. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/greenlet/tests/test_version.py:36
- **Description:** os.popen()
- **Evidence (Line):** `with os.popen(invoke_setup) as f:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 70. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/griffe/_internal/extensions/dataclasses.py:61
- **Description:** eval()
- **Evidence (Line):** `args.update({ast.literal_eval(str(key)): value for key, value in zip(expr.keys, expr.values, strict=`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 71. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/griffe/_internal/extensions/unpack_typeddict.py:90
- **Description:** eval()
- **Evidence (Line):** `total = ast.literal_eval(str(value))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 72. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_urls.py:336
- **Description:** Password Assignment detected
- **Evidence (Line):** `username="jo@gmail.com", password="a secret"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 73. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/httpx2/_urls.py:352
- **Description:** Password Assignment detected
- **Evidence (Line):** `username="jo@gmail.com", password="a secret"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 74. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/bccache.py:73
- **Description:** pickle load/dumps
- **Evidence (Line):** `checksum = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 75. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/bccache.py:79
- **Description:** marshal load
- **Evidence (Line):** `self.code = marshal.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 76. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/debug.py:145
- **Description:** exec()
- **Evidence (Line):** `exec(code, globals, locals)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 77. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/environment.py:1228
- **Description:** exec()
- **Evidence (Line):** `exec(code, namespace)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 78. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/lexer.py:663
- **Description:** eval()
- **Evidence (Line):** `value = literal_eval(value_str.replace("_", ""))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 79. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/nativetypes.py:40
- **Description:** eval()
- **Evidence (Line):** `return literal_eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 80. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/nodes.py:581
- **Description:** eval()
- **Evidence (Line):** `representation (objects where ``eval(repr(x)) == x`` is true).`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 81. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/_store_backends.py:196
- **Description:** pickle load/dumps
- **Evidence (Line):** `item = numpy_pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 82. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/_store_backends.py:198
- **Description:** pickle load/dumps
- **Evidence (Line):** `item = numpy_pickle.load(filename, mmap_mode=mmap_mode)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 83. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/externals/loky/backend/fork_exec.py:12
- **Description:** exec()
- **Evidence (Line):** `def fork_exec(cmd, keep_fds, env=None):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 84. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/externals/loky/backend/fork_exec.py:46
- **Description:** exec()
- **Evidence (Line):** `return _posixsubprocess.fork_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 85. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/externals/loky/backend/popen_loky_posix.py:128
- **Description:** exec()
- **Evidence (Line):** `pid = fork_exec(cmd_python, self._fds, env=process_obj.env)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 86. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/externals/loky/backend/popen_loky_posix.py:174
- **Description:** pickle load/dumps
- **Evidence (Line):** `prep_data = pickle.load(from_parent)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 87. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/externals/loky/backend/popen_loky_posix.py:176
- **Description:** pickle load/dumps
- **Evidence (Line):** `process_obj = pickle.load(from_parent)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 88. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/hashing.py:231
- **Description:** pickle load/dumps
- **Evidence (Line):** `# ``pickle.loads(pickle.dumps(np.dtype('f4'))) is not`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 89. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/hashing.py:236
- **Description:** pickle load/dumps
- **Evidence (Line):** `# and ``[np.dtype('f4'), pickle.loads(pickle.dumps('f4'))]``.`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 90. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/memory.py:178
- **Description:** eval()
- **Evidence (Line):** `(namely eval(repr(memorized_instance)) works).`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 91. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/memory.py:1192
- **Description:** eval()
- **Evidence (Line):** `def eval(self, func, *args, **kwargs):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 92. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/parallel.py:1771
- **Description:** eval()
- **Evidence (Line):** `def _wait_retrieval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 93. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/parallel.py:1800
- **Description:** eval()
- **Evidence (Line):** `while self._wait_retrieval():`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 94. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_func_inspect.py:366
- **Description:** exec()
- **Evidence (Line):** `exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 95. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:350
- **Description:** pickle load/dumps
- **Evidence (Line):** `c = pickle.loads(pickle.dumps(b))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 96. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:370
- **Description:** pickle load/dumps
- **Evidence (Line):** `dt1_roundtripped = pickle.loads(pickle.dumps(dt1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 97. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:383
- **Description:** pickle load/dumps
- **Evidence (Line):** `complex_dt1_roundtripped = pickle.loads(pickle.dumps(complex_dt1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 98. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:129
- **Description:** eval()
- **Evidence (Line):** `assert memory.eval(f, 1) == out`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 99. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:400
- **Description:** eval()
- **Evidence (Line):** `a1 = eval("lambda x: x")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 100. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:402
- **Description:** eval()
- **Evidence (Line):** `b1 = eval("lambda x: x+1")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 101. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:430
- **Description:** eval()
- **Evidence (Line):** `def test_memory_eval(tmpdir):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 102. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:434
- **Description:** eval()
- **Evidence (Line):** `m = eval("lambda x: x")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 103. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:166
- **Description:** exec()
- **Evidence (Line):** `exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 104. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:257
- **Description:** exec()
- **Evidence (Line):** `exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 105. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:686
- **Description:** pickle load/dumps
- **Evidence (Line):** `h = pickle.loads(pickle.dumps(g))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 106. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:692
- **Description:** pickle load/dumps
- **Evidence (Line):** `memory2 = pickle.loads(pickle.dumps(memory))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 107. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:697
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(pickle.dumps(memory))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 108. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:699
- **Description:** pickle load/dumps
- **Evidence (Line):** `gp = pickle.loads(pickle.dumps(g))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 109. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:792
- **Description:** pickle load/dumps
- **Evidence (Line):** `result2 = pickle.load(fp)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 110. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:1425
- **Description:** pickle load/dumps
- **Evidence (Line):** `memorized_result_loads = pickle.loads(memorized_result_pickle)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 111. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:1459
- **Description:** pickle load/dumps
- **Evidence (Line):** `memory_reloaded = pickle.loads(pickle.dumps(memory))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 112. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:1472
- **Description:** pickle load/dumps
- **Evidence (Line):** `func_cached_reloaded = pickle.loads(pickle.dumps(func_cached))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 113. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory.py:1485
- **Description:** pickle load/dumps
- **Evidence (Line):** `memorized_result_reloaded = pickle.loads(pickle.dumps(memorized_result))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 114. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_memory_async.py:69
- **Description:** eval()
- **Evidence (Line):** `evaled = await memory.eval(f, 1)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 115. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:119
- **Description:** pickle load/dumps
- **Evidence (Line):** `_member = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 116. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:159
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_ = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 117. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:172
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_ = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 118. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:185
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_loaded = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 119. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:197
- **Description:** pickle load/dumps
- **Evidence (Line):** `arr_reloaded = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 120. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:208
- **Description:** pickle load/dumps
- **Evidence (Line):** `b = numpy_pickle.load(filename, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 121. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:216
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_loaded = numpy_pickle.load(filename, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 122. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:229
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_loaded = numpy_pickle.load(filename, mmap_mode="r+")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 123. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:235
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(filename, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 124. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:240
- **Description:** pickle load/dumps
- **Evidence (Line):** `numpy_pickle.load(filename, mmap_mode="w+")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 125. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:257
- **Description:** pickle load/dumps
- **Evidence (Line):** `a_clone, b_clone = numpy_pickle.load(filename, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 126. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:312
- **Description:** pickle load/dumps
- **Evidence (Line):** `loaded = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 127. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:326
- **Description:** pickle load/dumps
- **Evidence (Line):** `b = numpy_pickle.load(filename, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 128. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:338
- **Description:** pickle load/dumps
- **Evidence (Line):** `reloaded_obj = numpy_pickle.load(this_filename, mmap_mode="r+")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 129. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:392
- **Description:** pickle load/dumps
- **Evidence (Line):** `result_list = numpy_pickle.load(fname)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 130. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:415
- **Description:** pickle load/dumps
- **Evidence (Line):** `le_array_native_load, be_array_native_load = numpy_pickle.load(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 131. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:422
- **Description:** pickle load/dumps
- **Evidence (Line):** `le_array_nonnative_load, be_array_nonnative_load = numpy_pickle.load(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 132. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:437
- **Description:** pickle load/dumps
- **Evidence (Line):** `numpy_pickle.load(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 133. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:465
- **Description:** pickle load/dumps
- **Evidence (Line):** `result_list = numpy_pickle.load(filename, mmap_mode=mmap_mode)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 134. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:529
- **Description:** pickle load/dumps
- **Evidence (Line):** `numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 135. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:719
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(dump_filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 136. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:763
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(filename_raw)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 137. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:794
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(dump_fname)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 138. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:815
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 139. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:820
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded_2 = numpy_pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 140. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:836
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 141. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:852
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj_reloaded = numpy_pickle.load(f, mmap_mode="r+")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 142. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:867
- **Description:** pickle load/dumps
- **Evidence (Line):** `numpy_pickle.load(f, mmap_mode="r+")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 143. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:884
- **Description:** pickle load/dumps
- **Evidence (Line):** `numpy_pickle.load(buf, mmap_mode="r+")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 144. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1008
- **Description:** pickle load/dumps
- **Evidence (Line):** `c = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 145. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1017
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert numpy_pickle.load(filename) == value`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 146. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1019
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert numpy_pickle.load(Path(filename)) == value`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 147. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1036
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert numpy_pickle.load(path) == value`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 148. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1053
- **Description:** pickle load/dumps
- **Evidence (Line):** `array_reloaded = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 149. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1067
- **Description:** pickle load/dumps
- **Evidence (Line):** `array_reloaded = numpy_pickle.load(filename)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 150. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1088
- **Description:** pickle load/dumps
- **Evidence (Line):** `array_reloaded = numpy_pickle.load(cf)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 151. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1099
- **Description:** pickle load/dumps
- **Evidence (Line):** `array_reloaded = numpy_pickle.load(cf)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 152. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1114
- **Description:** pickle load/dumps
- **Evidence (Line):** `memmaps = numpy_pickle.load(fname, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 153. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1217
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert numpy_pickle.load(fname) == data`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 154. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1223
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert numpy_pickle.load(fname) == data`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 155. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1254
- **Description:** pickle load/dumps
- **Evidence (Line):** `memmap = numpy_pickle.load(fname, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 156. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1270
- **Description:** pickle load/dumps
- **Evidence (Line):** `l_reloaded = numpy_pickle.load(fname, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 157. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_numpy_pickle.py:1293
- **Description:** pickle load/dumps
- **Evidence (Line):** `d_reloaded = numpy_pickle.load(fname, mmap_mode="r")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 158. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_store_backends.py:33
- **Description:** pickle load/dumps
- **Evidence (Line):** `reloaded = cpickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 159. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_utils.py:9
- **Description:** exec()
- **Evidence (Line):** `"exec('import os')",`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 160. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/jsonschema/tests/test_deprecations.py:396
- **Description:** eval()
- **Evidence (Line):** `def test_automatic_remote_retrieval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 161. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/documents/base.py:7
- **Description:** eval()
- **Evidence (Line):** `- `Document`: Text content for retrieval (RAG, vector stores, semantic search)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 162. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/langgraph/checkpoint/serde/jsonplus.py:310
- **Description:** pickle load/dumps
- **Evidence (Line):** `return pickle.loads(data_)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 163. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/langsmith/client.py:234
- **Description:** API Key Assignment detected
- **Evidence (Line):** `_ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 164. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/llama_index/core/base/base_retriever.py:121
- **Description:** eval()
- **Evidence (Line):** `def _handle_recursive_retrieval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 165. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/llama_index/core/base/base_retriever.py:155
- **Description:** eval()
- **Evidence (Line):** `async def _ahandle_recursive_retrieval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 166. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/llama_index/core/base/base_retriever.py:217
- **Description:** eval()
- **Evidence (Line):** `nodes = self._handle_recursive_retrieval(query_bundle, nodes)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 167. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/llama_index/core/base/base_retriever.py:248
- **Description:** eval()
- **Evidence (Line):** `nodes = await self._ahandle_recursive_retrieval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 168. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/llama_index/core/indices/query/query_transform/feedback_transform.py:33
- **Description:** eval()
- **Evidence (Line):** `eval(Evaluation): An evaluation object.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 169. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/mcp/cli/cli.py:48
- **Description:** subprocess with shell=True
- **Evidence (Line):** `subprocess.run([cmd, "--version"], check=True, capture_output=True, shell=True)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 170. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/more_itertools/recipes.py:1106
- **Description:** eval()
- **Evidence (Line):** `def polynomial_eval(coefficients, x):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 171. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/more_itertools/recipes.py:1115
- **Description:** eval()
- **Evidence (Line):** `>>> polynomial_eval(coefficients, x)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 172. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/msal/__main__.py:154
- **Description:** Password Assignment detected
- **Evidence (Line):** `_input("username: "), getpass.getpass("password: "), scopes=_input_scopes()))`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 173. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/msal/application.py:341
- **Description:** Private Key (PKCS8) detected
- **Evidence (Line):** `"private_key": "...-----BEGIN PRIVATE KEY-----... in PEM format",`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 174. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/msal/application.py:597
- **Description:** pickle load/dumps
- **Evidence (Line):** `persisted_http_cache = pickle.load(f)  # Take a snapshot`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 175. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/mudfish/_chrome/resources/accessibility/reading_mode_gdocs_helper/gdocs_script.js:19
- **Description:** eval()
- **Evidence (Line):** `eval(sanitized);`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 176. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/edgelist.py:288
- **Description:** eval()
- **Evidence (Line):** `edgedata = dict(literal_eval(" ".join(d)))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 177. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:183
- **Description:** eval()
- **Evidence (Line):** `def _q_merge_delta_via_full_eval(G, C_a, C_b, rest, red, resolution=1, weight="weight"):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 178. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:206
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, {u}, B, [{1, 2, 3}], red)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 179. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:219
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, {u}, B, [{0, 1, 3}], red)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 180. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:236
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 181. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:253
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 182. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:268
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red, resolution=gamma)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 183. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:288
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, A, B, rest, red)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 184. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/bipartite/tests/test_community.py:308
- **Description:** eval()
- **Evidence (Line):** `q_delta = _q_merge_delta_via_full_eval(G, A, B, [], red)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 185. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/flow/tests/test_maxflow_large_graph.py:56
- **Description:** pickle load/dumps
- **Evidence (Line):** `G = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 186. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/flow/tests/test_mincost.py:469
- **Description:** pickle load/dumps
- **Evidence (Line):** `G = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 187. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/flow/tests/test_networksimplex.py:180
- **Description:** pickle load/dumps
- **Evidence (Line):** `G = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 188. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/operators/tests/test_all.py:28
- **Description:** eval()
- **Evidence (Line):** `assert ghj.nodes[n] == eval(graph).nodes[int(node)]`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 189. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/algorithms/operators/tests/test_binary.py:23
- **Description:** eval()
- **Evidence (Line):** `assert gh.nodes[n] == eval(graph).nodes[int(node)]`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 190. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_coreviews.py:16
- **Description:** pickle load/dumps
- **Evidence (Line):** `pview = pickle.loads(pickle.dumps(view, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 191. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_coreviews.py:19
- **Description:** pickle load/dumps
- **Evidence (Line):** `pview = pickle.loads(pickle.dumps(view))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 192. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_coreviews.py:73
- **Description:** pickle load/dumps
- **Evidence (Line):** `pview = pickle.loads(pickle.dumps(view, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 193. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_coreviews.py:153
- **Description:** pickle load/dumps
- **Evidence (Line):** `pview = pickle.loads(pickle.dumps(view, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 194. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_coreviews.py:211
- **Description:** pickle load/dumps
- **Evidence (Line):** `pview = pickle.loads(pickle.dumps(view, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 195. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graph.py:268
- **Description:** pickle load/dumps
- **Evidence (Line):** `H = pickle.loads(pickle.dumps(G, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 196. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graph.py:677
- **Description:** pickle load/dumps
- **Evidence (Line):** `pg = pickle.loads(pickle.dumps(G, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 197. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graph.py:679
- **Description:** pickle load/dumps
- **Evidence (Line):** `pg = pickle.loads(pickle.dumps(G))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 198. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graphviews.py:18
- **Description:** pickle load/dumps
- **Evidence (Line):** `prv = pickle.loads(pickle.dumps(rv, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 199. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graphviews.py:65
- **Description:** pickle load/dumps
- **Evidence (Line):** `prv = pickle.loads(pickle.dumps(rv, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 200. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graphviews.py:118
- **Description:** pickle load/dumps
- **Evidence (Line):** `pdv = pickle.loads(pickle.dumps(dv, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 201. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graphviews.py:157
- **Description:** pickle load/dumps
- **Evidence (Line):** `puv = pickle.loads(pickle.dumps(uv, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 202. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_graphviews.py:206
- **Description:** pickle load/dumps
- **Evidence (Line):** `H = pickle.loads(pickle.dumps(G, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 203. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:22
- **Description:** pickle load/dumps
- **Evidence (Line):** `pnv = pickle.loads(pickle.dumps(nv, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 204. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:93
- **Description:** pickle load/dumps
- **Evidence (Line):** `pnv = pickle.loads(pickle.dumps(nv, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 205. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:278
- **Description:** pickle load/dumps
- **Evidence (Line):** `pev = pickle.loads(pickle.dumps(ev, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 206. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:568
- **Description:** pickle load/dumps
- **Evidence (Line):** `pev = pickle.loads(pickle.dumps(ev, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 207. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:1027
- **Description:** pickle load/dumps
- **Evidence (Line):** `pdeg = pickle.loads(pickle.dumps(deg, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 208. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:1416
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(pickle.dumps(G, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 209. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:1427
- **Description:** pickle load/dumps
- **Evidence (Line):** `ev = pickle.loads(pickle.dumps(G.edges, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 210. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:1430
- **Description:** pickle load/dumps
- **Evidence (Line):** `dv = pickle.loads(pickle.dumps(G.degree, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 211. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/classes/tests/test_reportviews.py:1434
- **Description:** pickle load/dumps
- **Evidence (Line):** `ev = pickle.loads(pickle.dumps(graph_class([(0, 1), (1, 2)]).edges, -1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 212. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/readwrite/edgelist.py:316
- **Description:** eval()
- **Evidence (Line):** `edgedata = dict(literal_eval(edgedata_str.strip()))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 213. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/readwrite/gml.py:106
- **Description:** eval()
- **Evidence (Line):** `return literal_eval(rep)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 214. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/readwrite/multiline_adjlist.py:324
- **Description:** eval()
- **Evidence (Line):** `edgedata = literal_eval(data)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 215. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/readwrite/tests/test_gml.py:454
- **Description:** eval()
- **Evidence (Line):** `data.append(literal_eval("{2.3j, 1 - 2.3j, ()}"))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 216. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/tests/test_lazy_imports.py:83
- **Description:** exec()
- **Evidence (Line):** `exec(s, {}, locls)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 217. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/networkx/utils/decorators.py:916
- **Description:** exec()
- **Evidence (Line):** `exec(compiled, globl, locl)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 218. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/utils/tests/test_backends.py:28
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert pickle.loads(pickled) is func.__wrapped__`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 219. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/utils/tests/test_backends.py:34
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert pickle.loads(pickled) is func`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 220. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/utils/tests/test_backends.py:37
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert pickle.loads(pickle.dumps(nx.inverse_line_graph)) is nx.inverse_line_graph`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 221. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/utils/tests/test_config.py:47
- **Description:** pickle load/dumps
- **Evidence (Line):** `cfg2 = pickle.loads(pickle.dumps(cfg))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 222. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/networkx/utils/tests/test_config.py:102
- **Description:** pickle load/dumps
- **Evidence (Line):** `cfg2 = pickle.loads(pickle.dumps(cfg))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 223. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/chunk/regexp.py:1329
- **Description:** eval()
- **Evidence (Line):** `def demo_eval(chunkparser, text):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 224. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/chunk/regexp.py:1419
- **Description:** eval()
- **Evidence (Line):** `demo_eval(cp, text)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 225. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/chunk/regexp.py:1428
- **Description:** eval()
- **Evidence (Line):** `demo_eval(cp, text)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 226. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/chunk/regexp.py:1435
- **Description:** eval()
- **Evidence (Line):** `demo_eval(cp, text)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 227. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/chunk/regexp.py:1445
- **Description:** eval()
- **Evidence (Line):** `demo_eval(cp, text)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 228. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/corpus/reader/comparative_sents.py:25
- **Description:** eval()
- **Evidence (Line):** `Proceedings of the ACM SIGIR International Conference on Information Retrieval`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 229. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/decorators.py:136
- **Description:** eval()
- **Evidence (Line):** `funcopy = eval(src, dict(_wrapper_=wrapper))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 230. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/decorators.py:204
- **Description:** eval()
- **Evidence (Line):** `dec_func = eval(src, dict(_func_=func, _call_=caller))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 231. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/internals.py:455
- **Description:** eval()
- **Evidence (Line):** `return eval(s[start_position : match.end()]), match.end()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 232. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/parse/evaluate.py:62
- **Description:** eval()
- **Evidence (Line):** `>>> las, uas = de.eval()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 233. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/parse/evaluate.py:88
- **Description:** eval()
- **Evidence (Line):** `def eval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 234. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/parse/transitionparser.py:812
- **Description:** eval()
- **Evidence (Line):** `>>> de.eval() >= (0, 0)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 235. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/parse/transitionparser.py:818
- **Description:** eval()
- **Evidence (Line):** `>>> de.eval() >= (0, 0)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 236. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/nltk/picklesec.py:71
- **Description:** pickle load/dumps
- **Evidence (Line):** `Convenience wrapper similar to pickle.load(file).`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 237. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/nltk/sem/chat80.py:615
- **Description:** shelve usage
- **Evidence (Line):** `db_out = shelve.open(db, "n")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 238. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/nltk/sem/chat80.py:635
- **Description:** shelve usage
- **Evidence (Line):** `db_in = shelve.open(db)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 239. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/tag/sequential.py:315
- **Description:** eval()
- **Evidence (Line):** `_context_to_tag = {ast.literal_eval(k): v for k, v in _context_to_tag.items()}`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 240. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:20
- **Description:** exec()
- **Evidence (Line):** `def _make_exec(path):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 241. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:31
- **Description:** exec()
- **Evidence (Line):** `_make_exec(cwd / _NAME / _NAME)  # attacker-planted ./<name>/<name>`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 242. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:33
- **Description:** exec()
- **Evidence (Line):** `_make_exec(realdir / _NAME)  # trusted, absolute location`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 243. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:45
- **Description:** exec()
- **Evidence (Line):** `_make_exec(cwd / _NAME / _NAME)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 244. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:47
- **Description:** exec()
- **Evidence (Line):** `_make_exec(realdir / _NAME)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 245. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:62
- **Description:** exec()
- **Evidence (Line):** `_make_exec(cwd / _NAME / _NAME)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 246. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:76
- **Description:** exec()
- **Evidence (Line):** `_make_exec(cwd / "tools" / _NAME)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 247. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_internals.py:91
- **Description:** exec()
- **Evidence (Line):** `_make_exec(cwd / "tools" / _NAME)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 248. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_pickle_allowlist_security.py:67
- **Description:** eval()
- **Evidence (Line):** `def test_allowlist_unpickler_directly_blocks_builtins_eval():`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 249. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_pickle_load_warnings.py:70
- **Description:** pickle load/dumps
- **Evidence (Line):** `# - no calls to pickle.load(...)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 250. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_pickle_load_warnings.py:82
- **Description:** pickle load/dumps
- **Evidence (Line):** `"Found a call to pickle.load(...) in nltk.app.chartparser_app; expected pickle_load(...)"`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 251. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_tnt.py:477
- **Description:** pickle load/dumps
- **Evidence (Line):** `restored = pickle.loads(pickle.dumps(tagger))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 252. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/tokenize/punkt.py:548
- **Description:** eval()
- **Evidence (Line):** `with eval(), which lists all the token's non-default`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 253. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/nltk/tokenize/texttiling.py:550
- **Description:** eval()
- **Evidence (Line):** `w = eval("numpy." + window + "(window_len)")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 254. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/_internal.py:204
- **Description:** eval()
- **Evidence (Line):** `newitem = (dtype, ast.literal_eval(repeats))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 255. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/arrayprint.py:1577
- **Description:** eval()
- **Evidence (Line):** `>>> assert eval(dtype_short_repr(dt)) == dt`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 256. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/records.py:703
- **Description:** pickle load/dumps
- **Evidence (Line):** `>>> pickle.loads(pickle.dumps(r))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 257. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test__exceptions.py:19
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.loads(pickle.dumps(error))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 258. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test__exceptions.py:84
- **Description:** pickle load/dumps
- **Evidence (Line):** `exc2 = pickle.loads(pickle.dumps(exc))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 259. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_arrayprint.py:343
- **Description:** eval()
- **Evidence (Line):** `assert_equal(eval(repr(a), vars(np)), a)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 260. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_arrayprint.py:344
- **Description:** eval()
- **Evidence (Line):** `assert_equal(eval(repr(a[0]), {'np': np}), a[0])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 261. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_custom_dtypes.py:504
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 262. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:912
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pickle.dumps(dt, protocol=proto)), dt)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 263. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:914
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pickle.dumps(dt, protocol=proto)), dt)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 264. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:916
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pickle.dumps(scalar, protocol=proto)),`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 265. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:919
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pickle.dumps(delta, protocol=proto)),`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 266. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:926
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pkl), np.dtype('<M8[7D]'))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 267. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:930
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pkl), np.dtype('<M8[W]'))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 268. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:934
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(pkl), np.dtype('>M8[us]'))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 269. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_datetime.py:941
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.loads(pickle.dumps(dt, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 270. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_dtype.py:996
- **Description:** eval()
- **Evidence (Line):** `assert_equal(np.dtype(eval(str(dt))), dt)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 271. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_dtype.py:1316
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickled = pickle.loads(buf)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 272. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_dtype.py:1387
- **Description:** pickle load/dumps
- **Evidence (Line):** `roundtrip_DType = pickle.loads(pickle.dumps(DType, proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 273. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_dtype.py:1398
- **Description:** pickle load/dumps
- **Evidence (Line):** `roundtrip_dt = pickle.loads(pickle.dumps(dt, proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 274. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:1704
- **Description:** eval()
- **Evidence (Line):** `assert_array_equal(eval(repr(xx), {"np": np, "array": np.array}), xx)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 275. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:4455
- **Description:** eval()
- **Evidence (Line):** `MyType = eval("type('MyType', (base,), class_namespace)",`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 276. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:11606
- **Description:** exec()
- **Evidence (Line):** `interp.exec("import numpy")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 277. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:194
- **Description:** pickle load/dumps
- **Evidence (Line):** `vals = pickle.loads(pickle.dumps(a, v))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 278. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:1856
- **Description:** pickle load/dumps
- **Evidence (Line):** `scalar = pickle.loads(pickle.dumps(scalar))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 279. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:2008
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(zs, pickle.loads(zs.dumps()))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 280. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:2015
- **Description:** pickle load/dumps
- **Evidence (Line):** `zs2 = pickle.loads(p)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 281. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:2024
- **Description:** pickle load/dumps
- **Evidence (Line):** `pk_load = pickle.loads(pk_dmp)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 282. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:2035
- **Description:** pickle load/dumps
- **Evidence (Line):** `array_from_buffer = pickle.loads(bytes_string, buffers=buffers)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 283. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:4953
- **Description:** pickle load/dumps
- **Evidence (Line):** `depickled_arr_with_object = pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 284. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:4955
- **Description:** pickle load/dumps
- **Evidence (Line):** `depickled_arr_without_object = pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 285. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:4978
- **Description:** pickle load/dumps
- **Evidence (Line):** `depickled_f_contiguous_array = pickle.loads(bytes_string,`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 286. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5009
- **Description:** pickle load/dumps
- **Evidence (Line):** `depickled_transposed_contiguous_array = pickle.loads(bytes_string,`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 287. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5025
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(x, pickle.loads(c_contiguous_dumped))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 288. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5027
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(x, pickle.loads(f_contiguous_dumped))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 289. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5029
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(x, pickle.loads(transposed_contiguous_dumped))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 290. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5031
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(x, pickle.loads(no_contiguous_dumped))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 291. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5043
- **Description:** pickle load/dumps
- **Evidence (Line):** `depickled_non_contiguous_array = pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 292. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5068
- **Description:** pickle load/dumps
- **Evidence (Line):** `a, pickle.loads(pickle.dumps(a, protocol=proto)),`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 293. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5077
- **Description:** pickle load/dumps
- **Evidence (Line):** `return pickle.loads(obj, encoding='latin1')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 294. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:5178
- **Description:** pickle load/dumps
- **Evidence (Line):** `new = pickle.loads(pickle.dumps(original_byte_reversed))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 295. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_multiarray.py:9146
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.loads(pickle_obj)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 296. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_overrides.py:221
- **Description:** pickle load/dumps
- **Evidence (Line):** `roundtripped = pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 297. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:184
- **Description:** eval()
- **Evidence (Line):** `recordarr_r = eval("np." + repr(recordarr), {'np': np})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 298. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:185
- **Description:** eval()
- **Evidence (Line):** `recarr_r = eval("np." + repr(recarr), {'np': np})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 299. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:187
- **Description:** eval()
- **Evidence (Line):** `recordview_r = eval("np." + repr(recordview), {'np': np, 'numpy': np})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 300. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:430
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(a, pickle.loads(pickle.dumps(a, protocol=proto)))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 301. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:431
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(a[0], pickle.loads(pickle.dumps(a[0],`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 302. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:437
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(a, pickle.loads(pickle.dumps(a, protocol=proto)))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 303. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:438
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(a[0], pickle.loads(pickle.dumps(a[0],`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 304. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:445
- **Description:** pickle load/dumps
- **Evidence (Line):** `pa = pickle.loads(pickle.dumps(a[0], protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 305. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_records.py:469
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(dump)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 306. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:57
- **Description:** pickle load/dumps
- **Evidence (Line):** `b = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 307. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:369
- **Description:** pickle load/dumps
- **Evidence (Line):** `dt_ = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 308. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:495
- **Description:** pickle load/dumps
- **Evidence (Line):** `result = pickle.loads(data, encoding='bytes')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 309. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:840
- **Description:** pickle load/dumps
- **Evidence (Line):** `new = pickle.loads(pickle.dumps(el, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 310. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1076
- **Description:** pickle load/dumps
- **Evidence (Line):** `y = pickle.loads(pickle.dumps(x, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 311. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1092
- **Description:** pickle load/dumps
- **Evidence (Line):** `xp = pickle.load(f, encoding='latin1')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 312. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1291
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_(pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 313. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1293
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_(pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 314. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1899
- **Description:** pickle load/dumps
- **Evidence (Line):** `data = pickle.loads(blob)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 315. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1911
- **Description:** pickle load/dumps
- **Evidence (Line):** `data = pickle.loads(pickle.dumps(data, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 316. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1932
- **Description:** pickle load/dumps
- **Evidence (Line):** `result = pickle.loads(data, encoding='latin1')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 317. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1961
- **Description:** pickle load/dumps
- **Evidence (Line):** `result = pickle.loads(data, encoding='latin1')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 318. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:1970
- **Description:** pickle load/dumps
- **Evidence (Line):** `result = pickle.loads(data, encoding='koi8-r')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 319. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:2215
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 320. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:2435
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_equal(pickle.loads(dumped), arr)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 321. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_regression.py:2569
- **Description:** pickle load/dumps
- **Evidence (Line):** `result = pickle.loads(test_data, encoding='bytes')`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 322. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_scalarmath.py:610
- **Description:** eval()
- **Evidence (Line):** `#            val2 = eval(val_repr)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 323. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_scalarmath.py:636
- **Description:** eval()
- **Evidence (Line):** `val2 = t(eval(val_repr))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 324. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:244
- **Description:** eval()
- **Evidence (Line):** `func = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 325. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:512
- **Description:** eval()
- **Evidence (Line):** `func = eval(intrin[:3])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 326. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:642
- **Description:** eval()
- **Evidence (Line):** `func = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 327. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:703
- **Description:** eval()
- **Evidence (Line):** `npyv_load_tillz, npyv_load_till = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 328. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:723
- **Description:** eval()
- **Evidence (Line):** `npyv_store_till = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 329. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:743
- **Description:** eval()
- **Evidence (Line):** `npyv_loadn = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 330. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:769
- **Description:** eval()
- **Evidence (Line):** `npyv_loadn_tillz, npyv_loadn_till = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 331. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:806
- **Description:** eval()
- **Evidence (Line):** `npyv_storen = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 332. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:845
- **Description:** eval()
- **Evidence (Line):** `npyv_storen_till = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 333. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:897
- **Description:** eval()
- **Evidence (Line):** `intrin = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 334. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_simd.py:1104
- **Description:** eval()
- **Evidence (Line):** `func = eval(intrin)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 335. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_stringdtype.py:659
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 336. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_ufunc.py:203
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_(pickle.loads(pickle.dumps(np.sin,`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 337. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_ufunc.py:208
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.loads(pickle.dumps(_rational_tests.test_add,`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 338. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_ufunc.py:215
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_(pickle.loads(astring) is np.cos)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 339. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_ufunc.py:224
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj = pickle.loads(pickle.dumps(_pickleable_module_global.ufunc))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 340. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_ufunc.py:499
- **Description:** pickle load/dumps
- **Evidence (Line):** `int64_2 = pickle.loads(pickle.dumps(int64))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 341. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_umath.py:513
- **Description:** eval()
- **Evidence (Line):** `a, b, divisors = eval(ex_val)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 342. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_umath.py:576
- **Description:** eval()
- **Evidence (Line):** `a = eval(ex_val)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 343. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_umath_accuracy.py:75
- **Description:** eval()
- **Evidence (Line):** `dtype=eval(datatype))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 344. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/_core/tests/test_umath_accuracy.py:78
- **Description:** eval()
- **Evidence (Line):** `dtype=eval(datatype))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 345. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/auxfuncs.py:632
- **Description:** eval()
- **Evidence (Line):** `return eval(f"{l1}:{' and '.join(l2)}")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 346. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/auxfuncs.py:640
- **Description:** eval()
- **Evidence (Line):** `return eval(f"{l1}:{' or '.join(l2)}")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 347. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/auxfuncs.py:644
- **Description:** eval()
- **Evidence (Line):** `return eval('lambda v,f=f:not f(v)')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 348. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/capi_maps.py:159
- **Description:** eval()
- **Evidence (Line):** `d = eval(f.read().lower(), {}, {})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 349. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/capi_maps.py:299
- **Description:** eval()
- **Evidence (Line):** `ret['size'] = repr(eval(ret['size']))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 350. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/capi_maps.py:447
- **Description:** eval()
- **Evidence (Line):** `v = eval(v, {}, {})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 351. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:1325
- **Description:** eval()
- **Evidence (Line):** `v = eval(initexpr, {}, params)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 352. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2272
- **Description:** eval()
- **Evidence (Line):** `def myeval(e, g=None, l=None):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 353. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2274
- **Description:** eval()
- **Evidence (Line):** `r = eval(e, g, l)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 354. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2305
- **Description:** eval()
- **Evidence (Line):** `c = int(myeval(e, {}, {}))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 355. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2326
- **Description:** eval()
- **Evidence (Line):** `b = myeval(ee, {}, {})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 356. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2331
- **Description:** eval()
- **Evidence (Line):** `a = myeval(ee, {}, {}) - b`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 357. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2336
- **Description:** eval()
- **Evidence (Line):** `c = myeval(ee, {}, {})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 358. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2342
- **Description:** eval()
- **Evidence (Line):** `c2 = myeval(ee, {}, {})`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 359. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2532
- **Description:** eval()
- **Evidence (Line):** `params[n] = param_eval(v, g_params, params, dimspec=dimspec)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 360. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2562
- **Description:** eval()
- **Evidence (Line):** `value = eval(value, {}, params)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 361. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2639
- **Description:** eval()
- **Evidence (Line):** `l = str(eval(l, {}, params))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 362. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2648
- **Description:** eval()
- **Evidence (Line):** `l = str(eval(l, {}, params))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 363. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2916
- **Description:** eval()
- **Evidence (Line):** `kindselect['kind'] = eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 364. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2966
- **Description:** eval()
- **Evidence (Line):** `def param_eval(v, g_params, params, dimspec=None):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 365. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:2987
- **Description:** eval()
- **Evidence (Line):** `p = eval(v, g_params, params)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 366. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:3018
- **Description:** eval()
- **Evidence (Line):** `item = eval(item, g_params, params)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 367. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/crackfortran.py:3470
- **Description:** eval()
- **Evidence (Line):** `v = eval(v)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 368. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/tests/test_crackfortran.py:378
- **Description:** eval()
- **Evidence (Line):** `ret = crackfortran.param_eval(v, g_params, params, dimspec=dimspec)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 369. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/tests/test_crackfortran.py:388
- **Description:** eval()
- **Evidence (Line):** `ret = crackfortran.param_eval(v, g_params, params, dimspec=dimspec)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 370. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/tests/test_crackfortran.py:407
- **Description:** eval()
- **Evidence (Line):** `ret = crackfortran.param_eval(v, g_params, params, dimspec=None)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 371. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/tests/test_f2py2e.py:889
- **Description:** exec()
- **Evidence (Line):** `def test_npd_f77exec():`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 372. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/f2py/tests/test_f2py2e.py:897
- **Description:** exec()
- **Evidence (Line):** `def test_npd_f90exec():`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 373. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:536
- **Description:** eval()
- **Evidence (Line):** `See :py:func:`ast.literal_eval()` for details.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 374. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:563
- **Description:** eval()
- **Evidence (Line):** `See :py:func:`ast.literal_eval()` for details.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 375. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:658
- **Description:** eval()
- **Evidence (Line):** `d = ast.literal_eval(header)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 376. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:663
- **Description:** eval()
- **Evidence (Line):** `d = ast.literal_eval(header)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 377. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:799
- **Description:** eval()
- **Evidence (Line):** `See :py:func:`ast.literal_eval()` for details.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 378. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:929
- **Description:** eval()
- **Evidence (Line):** `See :py:func:`ast.literal_eval()` for details.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 379. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_format_impl.py:838
- **Description:** pickle load/dumps
- **Evidence (Line):** `array = pickle.load(fp, **pickle_kwargs)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 380. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py:151
- **Description:** eval()
- **Evidence (Line):** `See :py:func:`ast.literal_eval()` for details.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 381. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py:356
- **Description:** eval()
- **Evidence (Line):** `See :py:func:`ast.literal_eval()` for details.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 382. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py:492
- **Description:** pickle load/dumps
- **Evidence (Line):** `"`allow_pickle=` keyword argument or `pickle.load()`.")`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 383. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py:494
- **Description:** pickle load/dumps
- **Evidence (Line):** `return pickle.load(fid, **pickle_kwargs)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 384. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_core.py:733
- **Description:** pickle load/dumps
- **Evidence (Line):** `a_pickled = pickle.loads(pickle.dumps(a, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 385. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_core.py:748
- **Description:** pickle load/dumps
- **Evidence (Line):** `a_pickled = pickle.loads(pickle.dumps(a, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 386. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_core.py:757
- **Description:** pickle load/dumps
- **Evidence (Line):** `mc_pickled = pickle.loads(pickle.dumps(mc, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 387. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_core.py:767
- **Description:** pickle load/dumps
- **Evidence (Line):** `a_pickled = pickle.loads(pickle.dumps(a, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 388. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_core.py:776
- **Description:** pickle load/dumps
- **Evidence (Line):** `test = pickle.loads(pickle.dumps(b, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 389. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_core.py:5738
- **Description:** pickle load/dumps
- **Evidence (Line):** `res = pickle.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 390. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_mrecords.py:291
- **Description:** pickle load/dumps
- **Evidence (Line):** `mrec_ = pickle.loads(_)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 391. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/ma/tests/test_old_ma.py:617
- **Description:** pickle load/dumps
- **Evidence (Line):** `y = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 392. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/matrixlib/tests/test_masked_matrix.py:89
- **Description:** pickle load/dumps
- **Evidence (Line):** `a_pickled = pickle.loads(pickle.dumps(a, protocol=proto))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 393. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:245
- **Description:** eval()
- **Evidence (Line):** `>>> hermeval(0,hermeline(3, 2))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 394. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:247
- **Description:** eval()
- **Evidence (Line):** `>>> hermeval(1,hermeline(3, 2))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 395. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:303
- **Description:** eval()
- **Evidence (Line):** `>>> hermeval((-1, 0, 1), coef)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 396. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:306
- **Description:** eval()
- **Evidence (Line):** `>>> hermeval((-1j, 1j), coef)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 397. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:790
- **Description:** eval()
- **Evidence (Line):** `tmp[0] += k[i] - hermeval(lbnd, tmp)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 398. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:796
- **Description:** eval()
- **Evidence (Line):** `def hermeval(x, c, tensor=True):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 399. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:856
- **Description:** eval()
- **Evidence (Line):** `>>> hermeval(1, coef)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 400. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:858
- **Description:** eval()
- **Evidence (Line):** `>>> hermeval([[1,2],[3,4]], coef)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 401. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:1138
- **Description:** eval()
- **Evidence (Line):** ```hermeval(x, c)`` are the same up to roundoff. This equivalence is`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 402. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/hermite_e.py:1407
- **Description:** eval()
- **Evidence (Line):** `>>> y = hermeval(x, [1, 2, 3]) + err`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 403. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:79
- **Description:** eval()
- **Evidence (Line):** `val1 = herme.hermeval(self.x, pol1)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 404. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:83
- **Description:** eval()
- **Evidence (Line):** `val2 = herme.hermeval(self.x, pol2)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 405. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:85
- **Description:** eval()
- **Evidence (Line):** `val3 = herme.hermeval(self.x, pol3)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 406. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:120
- **Description:** eval()
- **Evidence (Line):** `def test_hermeval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 407. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:122
- **Description:** eval()
- **Evidence (Line):** `assert_equal(herme.hermeval([], [1]).size, 0)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 408. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:130
- **Description:** eval()
- **Evidence (Line):** `res = herme.hermeval(x, [0] * i + [1])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 409. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:137
- **Description:** eval()
- **Evidence (Line):** `assert_equal(herme.hermeval(x, [1]).shape, dims)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 410. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:138
- **Description:** eval()
- **Evidence (Line):** `assert_equal(herme.hermeval(x, [1, 0]).shape, dims)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 411. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:139
- **Description:** eval()
- **Evidence (Line):** `assert_equal(herme.hermeval(x, [1, 0, 0]).shape, dims)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 412. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:258
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(-1, hermeint), i)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 413. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:379
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(v[..., i], herme.hermeval(x, coef))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 414. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:387
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(v[..., i], herme.hermeval(x, coef))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 415. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:444
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef3), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 416. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:447
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef3), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 417. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:451
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef4), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 418. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:454
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef4), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 419. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:458
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef4), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 420. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:487
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef1), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 421. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:489
- **Description:** eval()
- **Evidence (Line):** `assert_almost_equal(herme.hermeval(x, coef2), y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 422. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_hermite_e.py:535
- **Description:** eval()
- **Evidence (Line):** `res = herme.hermeval(roots, pol)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 423. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/polynomial/tests/test_polynomial.py:62
- **Description:** pickle load/dumps
- **Evidence (Line):** `y = pickle.loads(pickle.dumps(x))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 424. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_direct.py:328
- **Description:** pickle load/dumps
- **Evidence (Line):** `reloaded = pickle.loads(bitgen_pkl)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 425. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_direct.py:336
- **Description:** pickle load/dumps
- **Evidence (Line):** `aa = pickle.loads(pickle.dumps(ss))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 426. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_direct.py:346
- **Description:** pickle load/dumps
- **Evidence (Line):** `bg_plk = pickle.loads(pickle.dumps(bit_generator))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 427. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_direct.py:352
- **Description:** pickle load/dumps
- **Evidence (Line):** `bg_plk = pickle.loads(pickle.dumps(bit_generator))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 428. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_direct.py:580
- **Description:** pickle load/dumps
- **Evidence (Line):** `sfc = pickle.load(gz)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 429. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_generator_mt19937.py:2802
- **Description:** pickle load/dumps
- **Evidence (Line):** `rg_plk = pickle.loads(pickle.dumps(rg))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 430. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_generator_mt19937.py:2808
- **Description:** pickle load/dumps
- **Evidence (Line):** `rg_plk = pickle.loads(pickle.dumps(rg))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 431. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_generator_mt19937.py:2824
- **Description:** pickle load/dumps
- **Evidence (Line):** `rg = pickle.load(gz)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 432. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_randomstate.py:272
- **Description:** pickle load/dumps
- **Evidence (Line):** `rs_unpick = pickle.loads(pickle.dumps(random_state))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 433. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_smoke.py:488
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpick = pickle.loads(pick)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 434. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/random/tests/test_smoke.py:494
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpick = pickle.loads(pick)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 435. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/testing/_private/utils.py:1352
- **Description:** exec()
- **Evidence (Line):** `exec(astr, dict)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 436. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/testing/_private/utils.py:1640
- **Description:** exec()
- **Evidence (Line):** `exec(code, globs, locs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 437. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/numpy/tests/test_public_api.py:322
- **Description:** eval()
- **Evidence (Line):** `eval(module_name)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 438. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/numpy/tests/test_reloading.py:40
- **Description:** pickle load/dumps
- **Evidence (Line):** `assert_(pickle.loads(pickle.dumps(np._NoValue,`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 439. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/packaging/_parser.py:397
- **Description:** eval()
- **Evidence (Line):** `value = ast.literal_eval(python_str)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 440. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/packaging/_structures.py:10
- **Description:** pickle load/dumps
- **Evidence (Line):** `stand-in classes so that ``pickle.loads()`` can resolve those references.`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 441. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_caller.py:197
- **Description:** exec()
- **Evidence (Line):** `return self._hookexec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 442. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_caller.py:222
- **Description:** exec()
- **Evidence (Line):** `res = self._hookexec(self.name, self._hookimpls.copy(), kwargs, False)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 443. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_caller.py:262
- **Description:** exec()
- **Evidence (Line):** `return self._hookexec(self.name, hookimpls, kwargs, firstresult)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 444. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_caller.py:269
- **Description:** exec()
- **Evidence (Line):** `res = self._hookexec(self.name, [method], kwargs, False)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 445. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_manager.py:174
- **Description:** exec()
- **Evidence (Line):** `def _hookexec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 446. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_manager.py:183
- **Description:** exec()
- **Evidence (Line):** `return self._inner_hookexec(hook_name, methods, kwargs, firstresult)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 447. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pluggy/_manager.py:587
- **Description:** exec()
- **Evidence (Line):** `def traced_hookexec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 448. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/prance/util/formats.py:69
- **Description:** yaml.load (unsafe)
- **Evidence (Line):** `return yaml.load(str(spec_str))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 449. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pybars/_compiler.py:942
- **Description:** exec()
- **Evidence (Line):** `exec(compile(container.full_code, filename, 'exec', dont_inherit=True), mod.__dict__)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 450. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pybars/_compiler.py:956
- **Description:** exec()
- **Evidence (Line):** `exec(code + '\nresult = render(context, helpers=helpers, partials=partials, root=root)', ns)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 451. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_decorators.py:566
- **Description:** eval()
- **Evidence (Line):** `sig = signature_no_eval(validator)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 452. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_decorators.py:604
- **Description:** eval()
- **Evidence (Line):** `sig = signature_no_eval(serializer)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 453. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_decorators.py:642
- **Description:** eval()
- **Evidence (Line):** `sig = signature_no_eval(serializer)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 454. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_decorators.py:674
- **Description:** eval()
- **Evidence (Line):** `sig = signature_no_eval(serializer)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 455. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_decorators.py:722
- **Description:** eval()
- **Evidence (Line):** `sig = signature_no_eval(unwrap_wrapped_function(function))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 456. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_decorators.py:746
- **Description:** eval()
- **Evidence (Line):** `sig = signature_no_eval(unwrap_wrapped_function(function))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 457. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_fields.py:694
- **Description:** eval()
- **Evidence (Line):** `sig = _typing_extra.signature_no_eval(default_factory)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 458. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:1967
- **Description:** eval()
- **Evidence (Line):** `sig = _typing_extra.signature_no_eval(function)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 459. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:1992
- **Description:** eval()
- **Evidence (Line):** `sig = _typing_extra.signature_no_eval(function)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 460. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2069
- **Description:** eval()
- **Evidence (Line):** `sig = _typing_extra.signature_no_eval(function)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 461. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_namespace_utils.py:37
- **Description:** eval()
- **Evidence (Line):** `return eval(typ, *ns)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 462. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_signature.py:90
- **Description:** eval()
- **Evidence (Line):** `present_params = signature_no_eval(init).parameters.values()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 463. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_typing_extra.py:575
- **Description:** eval()
- **Evidence (Line):** `def signature_no_eval(f: Callable[..., Any]) -> Signature:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 464. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_typing_extra.py:694
- **Description:** eval()
- **Evidence (Line):** `(unless you are familiar with how eval() and exec() work).  The`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 465. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_typing_extra.py:727
- **Description:** eval()
- **Evidence (Line):** `# the globalns and localns order so that eval() looks into`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 466. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_typing_extra.py:694
- **Description:** exec()
- **Evidence (Line):** `(unless you are familiar with how eval() and exec() work).  The`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 467. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/_internal/_validate_call.py:107
- **Description:** eval()
- **Evidence (Line):** `signature = signature_no_eval(self.function)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 468. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/deprecated/parse.py:54
- **Description:** pickle load/dumps
- **Evidence (Line):** `return pickle.loads(bb)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 469. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/json_schema.py:1692
- **Description:** eval()
- **Evidence (Line):** `if len(_typing_extra.signature_no_eval(json_schema_extra).parameters) > 1:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 470. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/types.py:1820
- **Description:** Password Assignment detected
- **Evidence (Line):** `user = User(username='scolvin', password='password1')`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 471. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/types.py:1847
- **Description:** Password Assignment detected
- **Evidence (Line):** `model = Model(password='IAmSensitive', password_bytes=b'IAmSensitiveBytes')`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 472. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/v1/parse.py:42
- **Description:** pickle load/dumps
- **Evidence (Line):** `return pickle.loads(bb)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 473. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/v1/utils.py:195
- **Description:** eval()
- **Evidence (Line):** `eval('__IPYTHON__')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 474. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pydantic/validate_call_decorator.py:28
- **Description:** eval()
- **Evidence (Line):** `_typing_extra.signature_no_eval(cast(_generate_schema.ValidateCallSupportedTypes, function))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 475. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pygments/formatters/__init__.py:91
- **Description:** eval()
- **Evidence (Line):** `this method is equivalent to running ``eval()`` on the input file. The formatter is`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 476. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pygments/formatters/__init__.py:103
- **Description:** exec()
- **Evidence (Line):** `exec(f.read(), custom_namespace)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 477. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pygments/lexers/__init__.py:154
- **Description:** exec()
- **Evidence (Line):** `exec(f.read(), custom_namespace)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 478. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pygments/lexers/_julia_builtins.py:150
- **Description:** eval()
- **Evidence (Line):** `v = eval(Symbol(compl.mod))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 479. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pygments/lexers/_julia_builtins.py:361
- **Description:** eval()
- **Evidence (Line):** `v = eval(Symbol(compl.mod))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 480. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pygments/lexers/special.py:115
- **Description:** eval()
- **Evidence (Line):** `val = ast.literal_eval(val)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 481. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:112
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.builder.exactly(-x)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 482. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:119
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('self.builder.exactly(x)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 483. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:151
- **Description:** eval()
- **Evidence (Line):** `_G_python_6, lastError = eval("int(''.join(hs), 16)", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 484. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:162
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval("int('0'+''.join(ds), 8)", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 485. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:176
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval("int(''.join(ds))", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 486. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:191
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('x in string.octdigits', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 487. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:196
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('x', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 488. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:208
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('x in string.hexdigits', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 489. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:213
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('x', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 490. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:226
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\\n"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 491. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:232
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\\r"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 492. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:238
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\\t"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 493. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:244
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\\b"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 494. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:250
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\\f"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 495. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:256
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('\'"\'', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 496. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:262
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\'"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 497. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:268
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('"\\\\"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 498. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:279
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('"\'"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 499. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:294
- **Description:** eval()
- **Evidence (Line):** `_G_python_6, lastError = eval('"\'"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 500. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:298
- **Description:** eval()
- **Evidence (Line):** `_G_python_8, lastError = eval('self.builder.exactly(c)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 501. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:306
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('\'"\'', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 502. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:331
- **Description:** eval()
- **Evidence (Line):** `_G_python_5, lastError = eval('\'"\'', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 503. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:335
- **Description:** eval()
- **Evidence (Line):** `_G_python_7, lastError = eval("self.builder.exactly(''.join(c))", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 504. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:353
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('xs.insert(0, x)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 505. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:355
- **Description:** eval()
- **Evidence (Line):** `_G_python_5, lastError = eval("''.join(xs)", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 506. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:363
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'<'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 507. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:375
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('self.applicationArgs()', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 508. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:378
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.builder.apply(name, self.name, *args)', self.globals, _locals), `
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 509. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:382
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'>'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 510. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:386
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.builder.apply(name, self.name)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 511. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:426
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'('", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 512. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:433
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval("')'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 513. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:437
- **Description:** eval()
- **Evidence (Line):** `_G_python_6, lastError = eval('e', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 514. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:441
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'['", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 515. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:448
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval("']'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 516. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:452
- **Description:** eval()
- **Evidence (Line):** `_G_python_6, lastError = eval('self.builder.listpattern(e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 517. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:464
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'~'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 518. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:469
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'~'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 519. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:476
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('self.builder.lookahead(e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 520. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:483
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('self.builder._not(e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 521. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:508
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('self.builder.many(e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 522. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:514
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('self.builder.many1(e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 523. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:520
- **Description:** eval()
- **Evidence (Line):** `_G_python_2, lastError = eval('self.builder.optional(e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 524. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:524
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('e', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 525. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:536
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.builder.bind(r, n)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 526. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:540
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('r', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 527. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:547
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("':'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 528. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:554
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('self.builder.bind(self.builder.apply("anything", self.name), n)', sel`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 529. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:572
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.builder.sequence(es)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 530. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:584
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval("'|'", self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 531. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:594
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('es.insert(0, e)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 532. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:596
- **Description:** eval()
- **Evidence (Line):** `_G_python_5, lastError = eval('self.builder._or(es)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 533. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:604
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('"=>"', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 534. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:608
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.ruleValueExpr()', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 535. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:616
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('"?("', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 536. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:620
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.semanticPredicateExpr()', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 537. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:628
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('"!("', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 538. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:632
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.semanticActionExpr()', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 539. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:649
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('n == requiredName', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 540. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:654
- **Description:** eval()
- **Evidence (Line):** `_G_python_6, lastError = eval('setattr(self, "name", n)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 541. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:660
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('"::="', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 542. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:667
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('self.builder.sequence([args, e])', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 543. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:671
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('args', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 544. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:691
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('n', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 545. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:698
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('n', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 546. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:706
- **Description:** eval()
- **Evidence (Line):** `_G_python_3, lastError = eval('self.builder.rule(n, self.builder._or([r] + rs))', self.globals, _loc`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 547. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:710
- **Description:** eval()
- **Evidence (Line):** `_G_python_1, lastError = eval('self.builder.rule(n, r)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 548. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/boot.py:730
- **Description:** eval()
- **Evidence (Line):** `_G_python_4, lastError = eval('self.builder.makeGrammar(rs)', self.globals, _locals), None`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 549. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/builder.py:146
- **Description:** eval()
- **Evidence (Line):** `return self._expr('python', 'eval(%r, self.globals, _locals), None' %(expr,))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 550. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/pymeta/builder.py:320
- **Description:** eval()
- **Evidence (Line):** `eval(code, mod.__dict__)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 551. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/regex/tests/test_regex.py:3775
- **Description:** pickle load/dumps
- **Evidence (Line):** `r = pickle.loads(p)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 552. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/rich/markup.py:190
- **Description:** eval()
- **Evidence (Line):** `meta_params = literal_eval(parameters)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 553. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/ruamel/yaml/util.py:196
- **Description:** yaml.load (unsafe)
- **Evidence (Line):** `return yaml.load(yaml_str, **kw), indent, block_seq_indent`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 554. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/array_api_compat/_internal.py:64
- **Description:** exec()
- **Evidence (Line):** `exec(f"from {mod.__name__} import *", objs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 555. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/array_api_compat/cupy/fft.py:7
- **Description:** exec()
- **Evidence (Line):** `exec("from cupy.fft import *", _n)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 556. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/array_api_compat/cupy/linalg.py:10
- **Description:** exec()
- **Evidence (Line):** `exec('from cupy.linalg import *', _n)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 557. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/main.py:650
- **Description:** eval()
- **Evidence (Line):** `fun_val, cub_val, ceq_val = _eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 558. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/main.py:697
- **Description:** eval()
- **Evidence (Line):** `fun_val, cub_val, ceq_val = _eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 559. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/main.py:840
- **Description:** eval()
- **Evidence (Line):** `fun_val, cub_val, ceq_val = _eval(pb, framework, step, options)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 560. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/main.py:1422
- **Description:** eval()
- **Evidence (Line):** `def _eval(pb, framework, step, options):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 561. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/main.py:1446
- **Description:** eval()
- **Evidence (Line):** `x, fun, maxcv = pb.best_eval(penalty)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 562. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/problem.py:80
- **Description:** eval()
- **Evidence (Line):** `def n_eval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 563. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/problem.py:560
- **Description:** eval()
- **Evidence (Line):** `def n_eval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 564. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/problem.py:886
- **Description:** eval()
- **Evidence (Line):** `x_best, fun_best, _ = self.best_eval(penalty)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 565. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/problem.py:947
- **Description:** eval()
- **Evidence (Line):** `def n_eval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 566. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_external/cobyqa/problem.py:1192
- **Description:** eval()
- **Evidence (Line):** `def best_eval(self, penalty):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 567. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_lib/_bunch.py:160
- **Description:** exec()
- **Evidence (Line):** `exec(s, namespace)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 568. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_lib/_elementwise_iterative_method.py:238
- **Description:** eval()
- **Evidence (Line):** `x = pre_func_eval(work)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 569. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_lib/_elementwise_iterative_method.py:261
- **Description:** eval()
- **Evidence (Line):** `post_func_eval(x, f, work)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 570. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/_lib/tests/test_bunch.py:59
- **Description:** pickle load/dumps
- **Evidence (Line):** `obj = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 571. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/datasets/_fetchers.py:79
- **Description:** pickle load/dumps
- **Evidence (Line):** `ascent = array(pickle.load(f))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 572. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/differentiate/_differentiate.py:449
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 573. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/differentiate/_differentiate.py:495
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(x, f, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 574. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/integrate/_ivp/tests/test_ivp.py:700
- **Description:** eval()
- **Evidence (Line):** `def test_t_eval():`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 575. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/integrate/_tanhsinh.py:399
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 576. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/integrate/_tanhsinh.py:413
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(x, fj, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 577. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/integrate/tests/test__quad_vec.py:146
- **Description:** eval()
- **Evidence (Line):** `def test_num_eval(self, quadrature):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 578. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_bsplines.py:160
- **Description:** eval()
- **Evidence (Line):** `def test_rndm_naive_eval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 579. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_bsplines.py:167
- **Description:** eval()
- **Evidence (Line):** `y_n = xp.stack([_naive_eval(x, t, c, k, xp=xp) for x in xx])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 580. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_bsplines.py:941
- **Description:** eval()
- **Evidence (Line):** `def _naive_eval(x, t, c, k, *, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 581. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_bsplines.py:1417
- **Description:** eval()
- **Evidence (Line):** `b1 = np.vectorize(lambda x: _naive_eval(x, t, c, k, xp=np))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 582. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_fitpack2.py:1586
- **Description:** eval()
- **Evidence (Line):** `z_spl = spl_eval(spl, x, y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 583. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_fitpack2.py:1615
- **Description:** eval()
- **Evidence (Line):** `z_spl = spl_eval(spl, x, y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 584. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_fitpack2.py:1651
- **Description:** eval()
- **Evidence (Line):** `z_spl = spl_eval(spl, x, y)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 585. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpnd.py:172
- **Description:** pickle load/dumps
- **Evidence (Line):** `ip2 = pickle.loads(pickle.dumps(ip))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 586. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpnd.py:413
- **Description:** pickle load/dumps
- **Evidence (Line):** `ip2 = pickle.loads(pickle.dumps(ip))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 587. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:858
- **Description:** eval()
- **Evidence (Line):** `def test_eval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 588. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:1460
- **Description:** eval()
- **Evidence (Line):** `def test_derivative_eval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 589. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2440
- **Description:** eval()
- **Evidence (Line):** `v2 = _ppoly2d_eval(c, (x, y), xi, yi)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 590. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2446
- **Description:** eval()
- **Evidence (Line):** `v2 = _ppoly2d_eval(c, (x, y), xi, yi, nu=nu)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 591. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2466
- **Description:** eval()
- **Evidence (Line):** `v2 = _ppoly3d_eval(c, (x, y, z), xi, yi, zi, nu=nu)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 592. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2486
- **Description:** eval()
- **Evidence (Line):** `v2 = _ppoly4d_eval(c, (x, y, z, u), xi, yi, zi, ui)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 593. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2689
- **Description:** eval()
- **Evidence (Line):** `def _ppoly2d_eval(c, xs, xnew, ynew, nu=None):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 594. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2725
- **Description:** eval()
- **Evidence (Line):** `def _ppoly3d_eval(c, xs, xnew, ynew, znew, nu=None):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 595. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2765
- **Description:** eval()
- **Evidence (Line):** `def _ppoly4d_eval(c, xs, xnew, ynew, znew, unew, nu=None):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 596. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2825
- **Description:** pickle load/dumps
- **Evidence (Line):** `y2 = pickle.loads(pickle.dumps(obj))(x_eval)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 597. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_interpolate.py:2850
- **Description:** pickle load/dumps
- **Evidence (Line):** `Z2 = pickle.loads(pickle.dumps(obj))(eval_points)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 598. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_polyint.py:789
- **Description:** eval()
- **Evidence (Line):** `def test_periodic_eval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 599. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/interpolate/tests/test_rbfinterp.py:459
- **Description:** pickle load/dumps
- **Evidence (Line):** `yitp2 = pickle.loads(pickle.dumps(interp))(xitp)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 600. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/odr/tests/test_odr.py:575
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(obj_pickle)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 601. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/odr/tests/test_odr.py:584
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(obj_pickle)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 602. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/odr/tests/test_odr.py:588
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(obj_pickle)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 603. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/odr/tests/test_odr.py:597
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(obj_pickle)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 604. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/odr/tests/test_odr.py:606
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads(obj_pickle)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 605. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_bracket.py:244
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 606. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_bracket.py:262
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(x, f, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 607. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_bracket.py:653
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 608. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_bracket.py:669
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(x, f, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 609. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_chandrupatla.py:152
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 610. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_chandrupatla.py:157
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(x, f, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 611. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_chandrupatla.py:427
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 612. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_chandrupatla.py:464
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(x, f, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 613. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_nonlin.py:1642
- **Description:** exec()
- **Evidence (Line):** `exec(wrapper, ns)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 614. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/_optimize.py:323
- **Description:** eval()
- **Evidence (Line):** `def eval(x):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 615. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/tests/test__differential_evolution.py:261
- **Description:** eval()
- **Evidence (Line):** `def test_best_solution_retrieval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 616. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/optimize/tests/test_constraints.py:183
- **Description:** eval()
- **Evidence (Line):** `bounds2 = eval(repr(Bounds(*args)))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 617. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:342
- **Description:** eval()
- **Evidence (Line):** `>>> filtered = cspline1d_eval(cspline1d(sig), time)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 618. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:396
- **Description:** eval()
- **Evidence (Line):** `>>> filtered = qspline1d_eval(qspline1d(sig), time)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 619. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:526
- **Description:** eval()
- **Evidence (Line):** `def cspline1d_eval(cj, newx, dx=1.0, x0=0):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 620. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:569
- **Description:** eval()
- **Evidence (Line):** `>>> filtered = cspline1d_eval(cspline1d(sig), time)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 621. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:592
- **Description:** eval()
- **Evidence (Line):** `res[cond1] = cspline1d_eval(cj, -newx[cond1])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 622. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:593
- **Description:** eval()
- **Evidence (Line):** `res[cond2] = cspline1d_eval(cj, 2 * (N - 1) - newx[cond2])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 623. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:607
- **Description:** eval()
- **Evidence (Line):** `def qspline1d_eval(cj, newx, dx=1.0, x0=0):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 624. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:652
- **Description:** eval()
- **Evidence (Line):** `>>> filtered = qspline1d_eval(qspline1d(sig), time)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 625. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:675
- **Description:** eval()
- **Evidence (Line):** `res[cond1] = qspline1d_eval(cj, -newx[cond1])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 626. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/_spline_filters.py:676
- **Description:** eval()
- **Evidence (Line):** `res[cond2] = qspline1d_eval(cj, 2 * (N - 1) - newx[cond2])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 627. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:164
- **Description:** eval()
- **Evidence (Line):** `def test_cspline1d_eval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 628. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:165
- **Description:** eval()
- **Evidence (Line):** `r = signal.cspline1d_eval(xp.asarray([0., 0], dtype=xp.float64),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 629. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:169
- **Description:** eval()
- **Evidence (Line):** `r = signal.cspline1d_eval(xp.asarray([1., 0, 1], dtype=xp.float64),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 630. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:174
- **Description:** eval()
- **Evidence (Line):** `r = signal.cspline1d_eval(xp.asarray([1.0, 0, 1], dtype=xp.float64),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 631. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:195
- **Description:** eval()
- **Evidence (Line):** `signal.cspline1d_eval(cj, xp.asarray(newx), dx=dx, x0=x[0]), newy`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 632. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:200
- **Description:** eval()
- **Evidence (Line):** `signal.cspline1d_eval(xp.asarray([], dtype=xp.float64),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 633. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:205
- **Description:** eval()
- **Evidence (Line):** `def test_qspline1d_eval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 634. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:206
- **Description:** eval()
- **Evidence (Line):** `xp_assert_close(signal.qspline1d_eval(xp.asarray([0., 0]), xp.asarray([0.])),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 635. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:209
- **Description:** eval()
- **Evidence (Line):** `xp_assert_equal(signal.qspline1d_eval(xp.asarray([1., 0, 1]), xp.asarray([])),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 636. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:214
- **Description:** eval()
- **Evidence (Line):** `r = signal.qspline1d_eval(xp.asarray([1.0, 0, 1], dtype=xp.float64),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 637. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:234
- **Description:** eval()
- **Evidence (Line):** `r = signal.qspline1d_eval(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 638. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_bsplines.py:241
- **Description:** eval()
- **Evidence (Line):** `signal.qspline1d_eval(xp.asarray([], dtype=xp.float64),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 639. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_signaltools.py:1686
- **Description:** eval()
- **Evidence (Line):** `y2 = signal.cspline1d_eval(cj, x2, dx=dx, x0=x[0])`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 640. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/signal/tests/test_signaltools.py:1704
- **Description:** eval()
- **Evidence (Line):** `ynew = signal.cspline1d_eval(cy, xnew)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 641. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/sparse/csgraph/tests/test_graph_laplacian.py:43
- **Description:** eval()
- **Evidence (Line):** `mat = eval(mat, dict(np=np, sparse=sparse))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 642. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/sparse/csgraph/tests/test_graph_laplacian.py:299
- **Description:** eval()
- **Evidence (Line):** `d[L] = eval(L)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 643. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/sparse/csgraph/tests/test_graph_laplacian.py:301
- **Description:** eval()
- **Evidence (Line):** `d[L] = eval(L)(np.eye(n, dtype=mat.dtype))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 644. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/sparse/linalg/tests/test_interface.py:927
- **Description:** pickle load/dumps
- **Evidence (Line):** `B = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 645. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/sparse/tests/test_base.py:2334
- **Description:** pickle load/dumps
- **Evidence (Line):** `sploaded = pickle.loads(pickle.dumps(datsp, protocol=protocol))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 646. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:424
- **Description:** eval()
- **Evidence (Line):** `cdist(X1, X2, metric=eval(metric), **kwargs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 647. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:430
- **Description:** eval()
- **Evidence (Line):** `cdist(X1, X2, metric=eval(metric), *args)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 648. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:537
- **Description:** eval()
- **Evidence (Line):** `y2 = cdist(X1, X2, metric=eval(metric), **kwargs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 649. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:547
- **Description:** eval()
- **Evidence (Line):** `cdist(X1, X2, metric=eval(metric), **kwargs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 650. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:714
- **Description:** eval()
- **Evidence (Line):** `pdist(X1, metric=eval(metric), **kwargs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 651. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:720
- **Description:** eval()
- **Evidence (Line):** `pdist(X1, metric=eval(metric), *args)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 652. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:1352
- **Description:** eval()
- **Evidence (Line):** `y2 = pdist(X, metric=eval(metric), **kwargs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 653. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:1362
- **Description:** eval()
- **Evidence (Line):** `pdist(X, metric=eval(metric), **kwargs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 654. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_distance.py:2021
- **Description:** eval()
- **Evidence (Line):** `for m in [metric, eval(metric), "test_" + metric]:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 655. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_kdtree.py:911
- **Description:** pickle load/dumps
- **Evidence (Line):** `T2 = pickle.loads(tmp)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 656. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/tests/test_kdtree.py:925
- **Description:** pickle load/dumps
- **Evidence (Line):** `T2 = pickle.loads(tmp)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 657. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/transform/tests/test_rigid_transform.py:1502
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(pkl)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 658. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/spatial/transform/tests/test_rotation.py:2611
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(pkl)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 659. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/special/_precompute/wright_bessel.py:183
- **Description:** eval()
- **Evidence (Line):** `def eval(cls, n, rho, v):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 660. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/special/_precompute/wright_bessel.py:203
- **Description:** eval()
- **Evidence (Line):** `def eval(cls, m, rho, beta):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 661. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/special/_ufunc_tools.py:159
- **Description:** exec()
- **Evidence (Line):** `exec(code, namespace)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 662. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/special/tests/test_orthogonal.py:282
- **Description:** eval()
- **Evidence (Line):** `p = eval(pstr)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 663. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/special/tests/test_support_alternative_backends.py:326
- **Description:** pickle load/dumps
- **Evidence (Line):** `roundtrip = pickle.loads(pickle.dumps(func))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 664. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/_continued_fraction.py:325
- **Description:** eval()
- **Evidence (Line):** `def pre_func_eval(work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 665. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/_continued_fraction.py:329
- **Description:** eval()
- **Evidence (Line):** `def post_func_eval(n, ab, work):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 666. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/_continuous_distns.py:3482
- **Description:** eval()
- **Evidence (Line):** `def sk1_eval(c, *args):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 667. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/_continuous_distns.py:3494
- **Description:** eval()
- **Evidence (Line):** `def ku1_eval(c, *args):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 668. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/_distn_infrastructure.py:369
- **Description:** exec()
- **Evidence (Line):** `exec('del ' + obj)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 669. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/_distn_infrastructure.py:748
- **Description:** exec()
- **Evidence (Line):** `exec(self._parse_arg_template, ns)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 670. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/common_tests.py:294
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 671. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/common_tests.py:307
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(pkl)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 672. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/common_tests.py:317
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled_fit_function = pickle.loads(pickled_fit_function)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 673. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_axis_nan_policy.py:839
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled_hypotest = pickle.loads(pickled_hypotest)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 674. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_continued_fraction.py:144
- **Description:** eval()
- **Evidence (Line):** `def test_feval(self, xp):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 675. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_continuous.py:87
- **Description:** eval()
- **Evidence (Line):** `ref = eval(f'(a {left_comparison} x) & (x {right_comparison} b)')`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 676. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_continuous.py:2138
- **Description:** eval()
- **Evidence (Line):** `new_dist = eval(repr(dist))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 677. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_continuous.py:994
- **Description:** pickle load/dumps
- **Evidence (Line):** `dist3 = pickle.loads(pickle.dumps(dist1))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 678. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_distributions.py:6988
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 679. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_multivariate.py:4396
- **Description:** pickle load/dumps
- **Evidence (Line):** `unpickled = pickle.loads(s)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 680. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/scipy/stats/tests/test_sampling.py:256
- **Description:** pickle load/dumps
- **Evidence (Line):** `rng2 = pickle.loads(obj)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 681. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/semantic_kernel/connectors/ai/nvidia/README.md:20
- **Description:** API Key Assignment detected
- **Evidence (Line):** `api_key="your-nvidia-api-key", # Can also use NVIDIA_API_KEY env variable`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 682. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/semantic_kernel/connectors/ai/nvidia/README.md:42
- **Description:** API Key Assignment detected
- **Evidence (Line):** `api_key="your-nvidia-api-key", # Can also use NVIDIA_API_KEY env variable`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 683. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/semantic_kernel/connectors/in_memory.py:119
- **Description:** eval()
- **Evidence (Line):** `"""Evaluate a restricted filter AST without using eval()."""`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 684. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/semantic_kernel/connectors/memory_stores/azure_cognitive_search/utils.py:39
- **Description:** API Key Assignment detected
- **Evidence (Line):** `ENV_VAR_API_KEY = "AZURE_COGNITIVE_SEARCH_ADMIN_KEY"`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 685. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_distutils/command/bdist_rpm.py:369
- **Description:** os.popen()
- **Evidence (Line):** `out = os.popen(q_cmd)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 686. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_distutils/compilers/C/base.py:1130
- **Description:** eval()
- **Evidence (Line):** `if lib_type not in eval(expected):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 687. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_distutils/core.py:210
- **Description:** exec()
- **Evidence (Line):** `'script_name' is a file that will be read and run with 'exec()';`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 688. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_distutils/core.py:250
- **Description:** exec()
- **Evidence (Line):** `exec(code, g)  # noqa: S102 # executing the setup script is the point`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 689. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_vendor/jaraco/functools/__init__.py:563
- **Description:** eval()
- **Evidence (Line):** `return eval(use)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 690. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_vendor/more_itertools/recipes.py:1155
- **Description:** eval()
- **Evidence (Line):** `def polynomial_eval(coefficients, x):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 691. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_vendor/more_itertools/recipes.py:1164
- **Description:** eval()
- **Evidence (Line):** `>>> polynomial_eval(coefficients, x)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 692. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/_vendor/packaging/_parser.py:344
- **Description:** eval()
- **Evidence (Line):** `value = ast.literal_eval(python_str)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 693. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/build_meta.py:317
- **Description:** exec()
- **Evidence (Line):** `exec(code, locals())  # noqa: S102 # exec is intentional here`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 694. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/command/bdist_egg.py:396
- **Description:** marshal load
- **Evidence (Line):** `code = marshal.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 695. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/config/expand.py:72
- **Description:** eval()
- **Evidence (Line):** `ast.literal_eval(value)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 696. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/depends.py:132
- **Description:** marshal load
- **Evidence (Line):** `code = marshal.load(f)`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 697. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/launch.py:32
- **Description:** exec()
- **Evidence (Line):** `exec(code, namespace)  # noqa: S102 # exec is intentional here`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 698. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/wheel.py:191
- **Description:** eval()
- **Evidence (Line):** `def eval(req, **env):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 699. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/setuptools/wheel.py:212
- **Description:** eval()
- **Evidence (Line):** `(req for req in reqs if for_extra(req) and eval(req, extra=extra)),`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 700. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/six.py:740
- **Description:** exec()
- **Evidence (Line):** `exec("""exec _code_ in _globs_, _locs_""")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 701. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mssql/base.py:1857
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 702. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mssql/base.py:1918
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 703. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mysql/_mariadb_shim.py:81
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self) -> None:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 704. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mysql/mariadbconnector.py:103
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self) -> None:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 705. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mysql/mariadbconnector.py:104
- **Description:** exec()
- **Evidence (Line):** `super().post_exec()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 706. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/oracle/base.py:2078
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 707. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/oracle/cx_oracle.py:1117
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 708. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/oracle/cx_oracle.py:1118
- **Description:** exec()
- **Evidence (Line):** `super().pre_exec()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 709. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/oracle/cx_oracle.py:1128
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 710. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py:483
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 711. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/pg8000.py:327
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 712. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/psycopg2.py:568
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 713. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/base.py:1827
- **Description:** exec()
- **Evidence (Line):** `context.pre_exec()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 714. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/base.py:1967
- **Description:** exec()
- **Evidence (Line):** `context.post_exec()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 715. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/base.py:2134
- **Description:** exec()
- **Evidence (Line):** `context.post_exec()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 716. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/default.py:2042
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 717. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/default.py:2050
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 718. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/default.py:2070
- **Description:** exec()
- **Evidence (Line):** `calculated within post_exec().`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 719. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/interfaces.py:3189
- **Description:** exec()
- **Evidence (Line):** `sql.Compiled object by the time pre_exec() has completed."""`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 720. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/interfaces.py:3333
- **Description:** exec()
- **Evidence (Line):** `def pre_exec(self) -> None:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 721. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/interfaces.py:3379
- **Description:** exec()
- **Evidence (Line):** `def post_exec(self) -> None:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 722. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/ext/serializer.py:64
- **Description:** pickle load/dumps
- **Evidence (Line):** `pickle.loads()/dumps() can be used to fully dump any ``MetaData`` object,`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 723. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/ext/serializer.py:149
- **Description:** pickle load/dumps
- **Evidence (Line):** `cls = pickle.loads(b64decode(clsarg))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 724. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/ext/serializer.py:152
- **Description:** pickle load/dumps
- **Evidence (Line):** `cls = pickle.loads(b64decode(args))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 725. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/ext/serializer.py:155
- **Description:** pickle load/dumps
- **Evidence (Line):** `cls = pickle.loads(b64decode(args))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 726. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/ext/serializer.py:159
- **Description:** pickle load/dumps
- **Evidence (Line):** `cls = pickle.loads(b64decode(mapper))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 727. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/_orm_constructors.py:1323
- **Description:** eval()
- **Evidence (Line):** `registry of tables.  The Python ``eval()`` function is no longer`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 728. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/_orm_constructors.py:1559
- **Description:** eval()
- **Evidence (Line):** `argument is interpreted using Python's ``eval()`` function.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 729. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/_orm_constructors.py:1763
- **Description:** eval()
- **Evidence (Line):** `argument is interpreted using Python's ``eval()`` function.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 730. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/_orm_constructors.py:1860
- **Description:** eval()
- **Evidence (Line):** `argument is interpreted using Python's ``eval()`` function.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 731. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/_orm_constructors.py:1879
- **Description:** eval()
- **Evidence (Line):** `argument is interpreted using Python's ``eval()`` function.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 732. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/_orm_constructors.py:1921
- **Description:** eval()
- **Evidence (Line):** `argument is interpreted using Python's ``eval()`` function.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 733. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/bulk_persistence.py:694
- **Description:** exec()
- **Evidence (Line):** `def orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 734. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/bulk_persistence.py:1211
- **Description:** exec()
- **Evidence (Line):** `def orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 735. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/clsregistry.py:592
- **Description:** eval()
- **Evidence (Line):** `x = eval(self.arg, globals(), self._dict)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 736. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/context.py:295
- **Description:** exec()
- **Evidence (Line):** `def orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 737. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/context.py:345
- **Description:** exec()
- **Evidence (Line):** `def orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 738. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/context.py:506
- **Description:** exec()
- **Evidence (Line):** `def orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 739. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/events.py:1986
- **Description:** exec()
- **Evidence (Line):** `def after_flush_postexec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 740. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/session.py:2287
- **Description:** exec()
- **Evidence (Line):** `) = compile_state_cls.orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 741. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/session.py:2327
- **Description:** exec()
- **Evidence (Line):** `# now run orm_pre_session_exec() "for real".   if there were`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 742. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/session.py:2336
- **Description:** exec()
- **Evidence (Line):** `) = compile_state_cls.orm_pre_session_exec(`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 743. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/session.py:4674
- **Description:** exec()
- **Evidence (Line):** `self.dispatch.after_flush_postexec(self, flush_context)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 744. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/strategies.py:2923
- **Description:** exec()
- **Evidence (Line):** `def load_collection_from_joined_exec(state, dict_, row):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 745. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/orm/strategies.py:2962
- **Description:** exec()
- **Evidence (Line):** `def load_scalar_from_joined_exec(state, dict_, row):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 746. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/sql/lambdas.py:1264
- **Description:** exec()
- **Evidence (Line):** `exec(code, vars_, vars_)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 747. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/sql/sqltypes.py:2034
- **Description:** pickle load/dumps
- **Evidence (Line):** ```pickle.dumps()`` to incoming objects, and ``pickle.loads()`` on`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 748. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/testing/plugin/pytestplugin.py:671
- **Description:** exec()
- **Evidence (Line):** `exec(code, env)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 749. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py:455
- **Description:** exec()
- **Evidence (Line):** `exec(code, env)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 750. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py:2163
- **Description:** exec()
- **Evidence (Line):** `exec(code, env)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 751. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/typing.py:265
- **Description:** eval()
- **Evidence (Line):** `annotation = eval(expression, cls_namespace, locals_)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 752. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/typing.py:267
- **Description:** eval()
- **Evidence (Line):** `annotation = eval(expression, base_globals, locals_)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 753. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/typing.py:293
- **Description:** eval()
- **Evidence (Line):** `# name only, just look in globals.  eval() works perfectly fine here,`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 754. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlglot/executor/context.py:45
- **Description:** eval()
- **Evidence (Line):** `def eval(self, code):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 755. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlglot/executor/context.py:46
- **Description:** eval()
- **Evidence (Line):** `return eval(code, self.env)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 756. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlglot/executor/context.py:49
- **Description:** eval()
- **Evidence (Line):** `return tuple(self.eval(code) for code in codes)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 757. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlglot/executor/context.py:84
- **Description:** eval()
- **Evidence (Line):** `rows = [reader.row for reader, _ in self if self.eval(condition)]`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 758. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlglot/executor/python.py:257
- **Description:** eval()
- **Evidence (Line):** `if condition and not context.eval(condition):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 759. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlglot/executor/python.py:342
- **Description:** eval()
- **Evidence (Line):** `return condition_context.eval(condition) is True`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 760. [Critical] Hardcoded Secret
- **File:** .venv-test/lib/python3.12/site-packages/starlette/datastructures.py:182
- **Description:** Password Assignment detected
- **Evidence (Line):** `url = str(self.replace(password="********"))`
- **Exploit Scenario:** Attacker could extract credentials and gain unauthorized access
- **Fix Recommendation:** Move secrets to environment variables or secret manager, rotate compromised credentials
- **Confidence:** High

### 761. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/tqdm/cli.py:38
- **Description:** eval()
- **Evidence (Line):** `return literal_eval(f'"{val}"').encode()`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 762. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/tqdm/cli.py:301
- **Description:** eval()
- **Evidence (Line):** `t.update(literal_eval(i.decode()))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 763. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/tqdm/cli.py:304
- **Description:** eval()
- **Evidence (Line):** `t.update(literal_eval(i.decode()) - t.n)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 764. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/tqdm/cli.py:317
- **Description:** eval()
- **Evidence (Line):** `t.update(literal_eval(i.decode()))`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 765. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/tqdm/cli.py:320
- **Description:** eval()
- **Evidence (Line):** `t.update(literal_eval(i.decode()) - t.n)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 766. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:1591
- **Description:** eval()
- **Evidence (Line):** `(unless you are familiar with how eval() and exec() work).  The`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 767. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:4167
- **Description:** eval()
- **Evidence (Line):** `# as a way of emulating annotation scopes when calling `eval()``
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 768. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:4172
- **Description:** eval()
- **Evidence (Line):** `value if not isinstance(value, str) else eval(value, globals, locals)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 769. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:4219
- **Description:** eval()
- **Evidence (Line):** `# If we pass None to eval() below, the globals of this module are used.`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 770. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:4231
- **Description:** eval()
- **Evidence (Line):** `# as a way of emulating annotation scopes when calling `eval()``
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 771. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:4254
- **Description:** eval()
- **Evidence (Line):** `value = eval(code, globals, locals)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 772. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_extensions.py:1591
- **Description:** exec()
- **Evidence (Line):** `(unless you are familiar with how eval() and exec() work).  The`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 773. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_inspection/typing_objects.py:112
- **Description:** exec()
- **Evidence (Line):** `exec(func_code, globals_, locals_)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 774. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/typing_inspection/typing_objects.py:153
- **Description:** exec()
- **Evidence (Line):** `exec(func_code, globals_, locals_)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 775. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/websockets/cli.py:189
- **Description:** os.system()
- **Evidence (Line):** `os.system("")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 776. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:138
- **Description:** eval()
- **Evidence (Line):** `def eval(self, code: str) -> t.Any:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 777. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:139
- **Description:** eval()
- **Evidence (Line):** `return self.console.eval(code)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 778. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:396
- **Description:** eval()
- **Evidence (Line):** `return Response(frame.eval(command), mimetype="text/html")`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 779. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/console.py:213
- **Description:** eval()
- **Evidence (Line):** `def eval(self, code: str) -> str:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 780. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/console.py:177
- **Description:** exec()
- **Evidence (Line):** `exec(code, self.locals)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 781. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/tbtools.py:392
- **Description:** eval()
- **Evidence (Line):** `def eval(self, code: str) -> t.Any:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 782. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/tbtools.py:393
- **Description:** eval()
- **Evidence (Line):** `return self.console.eval(code)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 783. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/routing/rules.py:737
- **Description:** exec()
- **Evidence (Line):** `exec(code, globs, locs)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 784. [Critical] Insecure Deserialization
- **File:** .venv-test/lib/python3.12/site-packages/workflows/context/serializers.py:341
- **Description:** pickle load/dumps
- **Evidence (Line):** `return pickle.loads(base64.b64decode(value))`
- **Exploit Scenario:** Attacker could achieve remote code execution
- **Fix Recommendation:** Use safe serialization formats (JSON), avoid pickle/yaml.load with untrusted data
- **Confidence:** High

### 785. [Critical] Command Injection
- **File:** .venv-test/lib/python3.12/site-packages/wrapt/decorators.py:211
- **Description:** exec()
- **Evidence (Line):** `exec(f"def adapter{adapter}: pass", ns, ns)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 786. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/core/src/orchestration/orchestrator.rs:62
- **Description:** eval()
- **Evidence (Line):** `/// Orchestrate end-to-end retrieval (Stage 1 + Stage 2)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 787. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/core/src/quality_gates/mod.rs:48
- **Description:** eval()
- **Evidence (Line):** `/// Validate source before retrieval (metadata validation)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 788. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/core/src/quality_gates/mod.rs:70
- **Description:** eval()
- **Evidence (Line):** `/// Validate content after retrieval (quality validation)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 789. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/python/pystreammcp/integrations/llamaindex.py:286
- **Description:** eval()
- **Evidence (Line):** `Composes retrieval (via PyStreamMCP) with a simple synthesis step,`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 790. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/python/pystreammcp/retrieval/cli.py:94
- **Description:** eval()
- **Evidence (Line):** `def retrieval() -> None:`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 791. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/tests/selective_retrieval_tests.rs:300
- **Description:** eval()
- **Evidence (Line):** `fn test_concurrent_selective_retrieval() {`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 792. [Critical] Command Injection
- **File:** .worktrees/retrieval-adapters/tests/test_llamaindex_integration.py:145
- **Description:** eval()
- **Evidence (Line):** `def test_index_retrieval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 793. [Critical] Command Injection
- **File:** core/src/orchestration/orchestrator.rs:62
- **Description:** eval()
- **Evidence (Line):** `/// Orchestrate end-to-end retrieval (Stage 1 + Stage 2)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 794. [Critical] Command Injection
- **File:** core/src/quality_gates/mod.rs:48
- **Description:** eval()
- **Evidence (Line):** `/// Validate source before retrieval (metadata validation)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 795. [Critical] Command Injection
- **File:** core/src/quality_gates/mod.rs:70
- **Description:** eval()
- **Evidence (Line):** `/// Validate content after retrieval (quality validation)`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 796. [Critical] Command Injection
- **File:** python/pystreammcp/integrations/llamaindex.py:293
- **Description:** eval()
- **Evidence (Line):** `Composes retrieval (via PyStreamMCP) with a simple synthesis step,`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 797. [Critical] Command Injection
- **File:** tests/selective_retrieval_tests.rs:300
- **Description:** eval()
- **Evidence (Line):** `fn test_concurrent_selective_retrieval() {`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 798. [Critical] Command Injection
- **File:** tests/test_llamaindex_integration.py:145
- **Description:** eval()
- **Evidence (Line):** `def test_index_retrieval(self):`
- **Exploit Scenario:** Attacker could execute arbitrary system commands
- **Fix Recommendation:** Avoid shell execution, use subprocess with shell=False and list args
- **Confidence:** High

### 799. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/PIL/GdImageFile.py:77
- **Description:** Django raw SQL concatenation
- **Evidence (Line):** `self.palette = ImagePalette.raw(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 800. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/aiosqlite/tests/smoke.py:459
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `await db.execute(f"select 1, {i}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 801. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mssql/base.py:3277
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 802. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mssql/base.py:2001
- **Description:** SQL % formatting
- **Evidence (Line):** `self.cursor.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 803. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mysql/base.py:2853
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"SET SESSION TRANSACTION ISOLATION LEVEL {level}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 804. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mysql/mysqldb.py:184
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute("SET NAMES %s" % charset_name)`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 805. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/oracle/cx_oracle.py:1399
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"ALTER SESSION SET ISOLATION_LEVEL={level}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 806. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/oracle/provision.py:277
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute("ALTER SESSION SET CURRENT_SCHEMA=%s" % schema_name)`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 807. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/base.py:364
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute("SET SESSION search_path='%s'" % schema_name)`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 808. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/pg8000.py:368
- **Description:** SQL string concatenation
- **Evidence (Line):** `self.cursor.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 809. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/pg8000.py:579
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"""`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 810. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/pg8000.py:538
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 811. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/pg8000.py:559
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 812. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/provision.py:90
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute("SET SESSION search_path='%s'" % schema_name)`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 813. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/sqlite/base.py:2335
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"PRAGMA read_uncommitted = {isolation_level}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 814. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/sqlite/provision.py:122
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `dbapi_connection.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 815. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/sqlite/pysqlcipher.py:150
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"pragma key={passphrase}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 816. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/sqlite/pysqlcipher.py:152
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `cursor.execute(f"pragma {prag}={value}")`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 817. [High] SQL Injection
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/engine/base.py:3089
- **Description:** SQL % formatting
- **Evidence (Line):** `cursor.execute("use %s" % shards[shard_id])`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 818. [High] SQL Injection
- **File:** .worktrees/retrieval-adapters/python/pystreammcp/federation.py:97
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `self._conn.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 819. [High] SQL Injection
- **File:** .worktrees/retrieval-adapters/python/pystreammcp/federation.py:104
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `self._conn.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 820. [High] SQL Injection
- **File:** .worktrees/retrieval-adapters/python/pystreammcp/federation.py:112
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `self._conn.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 821. [High] SQL Injection
- **File:** python/pystreammcp/federation.py:97
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `self._conn.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 822. [High] SQL Injection
- **File:** python/pystreammcp/federation.py:104
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `self._conn.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 823. [High] SQL Injection
- **File:** python/pystreammcp/federation.py:112
- **Description:** SQL f-string interpolation
- **Evidence (Line):** `self._conn.execute(`
- **Exploit Scenario:** Attacker could manipulate SQL queries to access/modify/delete data
- **Fix Recommendation:** Use parameterized queries/prepared statements
- **Confidence:** Medium

### 824. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client.py:1357
- **Description:** SHA1 usage
- **Evidence (Line):** `match = base64.b64encode(hashlib.sha1(sec_key + WS_KEY).digest()).decode()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 825. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client.py:1357
- **Description:** Weak hash algorithm
- **Evidence (Line):** `match = base64.b64encode(hashlib.sha1(sec_key + WS_KEY).digest()).decode()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 826. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client_middleware_digest_auth.py:332
- **Description:** SHA1 usage
- **Evidence (Line):** `cnonce = hashlib.sha1(`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 827. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client_middleware_digest_auth.py:38
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"MD5": hashlib.md5,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 828. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client_middleware_digest_auth.py:39
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"MD5-SESS": hashlib.md5,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 829. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client_middleware_digest_auth.py:40
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"SHA": hashlib.sha1,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 830. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client_middleware_digest_auth.py:41
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"SHA-SESS": hashlib.sha1,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 831. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/client_middleware_digest_auth.py:332
- **Description:** Weak hash algorithm
- **Evidence (Line):** `cnonce = hashlib.sha1(`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 832. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/web_ws.py:338
- **Description:** SHA1 usage
- **Evidence (Line):** `hashlib.sha1(key.encode() + WS_KEY).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 833. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aiohttp/web_ws.py:338
- **Description:** Weak hash algorithm
- **Evidence (Line):** `hashlib.sha1(key.encode() + WS_KEY).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 834. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aioice/candidate.py:13
- **Description:** MD5 usage
- **Evidence (Line):** `return hashlib.md5(key.encode("ascii")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 835. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aioice/candidate.py:13
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.md5(key.encode("ascii")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 836. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aioice/turn.py:30
- **Description:** MD5 usage
- **Evidence (Line):** `return hashlib.md5(":".join([username, realm, password]).encode("utf8")).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 837. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/aioice/turn.py:30
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.md5(":".join([username, realm, password]).encode("utf8")).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 838. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/policies.py:134
- **Description:** MD5 usage
- **Evidence (Line):** `calculate_content_md5(response.http_response.body())`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 839. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/policies.py:406
- **Description:** MD5 usage
- **Evidence (Line):** `computed_md5 = encode_base64(calculate_content_md5(data))`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 840. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/policies.py:442
- **Description:** MD5 usage
- **Evidence (Line):** `calculate_content_md5(response.http_response.body())`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 841. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/policies_async.py:66
- **Description:** MD5 usage
- **Evidence (Line):** `calculate_content_md5(response.http_response.body())`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 842. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/validation.py:79
- **Description:** MD5 usage
- **Evidence (Line):** `def calculate_content_md5(data: Union[bytes, IO[bytes]]) -> bytes:`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 843. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/validation.py:80
- **Description:** MD5 usage
- **Evidence (Line):** `md5 = hashlib.md5(usedforsecurity=False)  # nosec`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 844. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/azure/storage/blob/_shared/validation.py:80
- **Description:** Weak hash algorithm
- **Evidence (Line):** `md5 = hashlib.md5(usedforsecurity=False)  # nosec`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 845. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/coverage/lcovreport.py:43
- **Description:** MD5 usage
- **Evidence (Line):** `hashed = hashlib.md5(line.encode("utf-8"), usedforsecurity=False).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 846. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/coverage/lcovreport.py:43
- **Description:** Weak hash algorithm
- **Evidence (Line):** `hashed = hashlib.md5(line.encode("utf-8"), usedforsecurity=False).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 847. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/backends/openssl/backend.py:39
- **Description:** DES usage
- **Evidence (Line):** `# FIPS 140-3. To keep it simple we denylist any use of TripleDES (TDEA).`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 848. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/decrepit/ciphers/algorithms.py:29
- **Description:** DES usage
- **Evidence (Line):** `class TripleDES(BlockCipherAlgorithm):`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 849. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/decrepit/ciphers/algorithms.py:40
- **Description:** DES usage
- **Evidence (Line):** `"Single-key TripleDES (8-byte keys) is deprecated and "`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 850. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/decrepit/ciphers/algorithms.py:49
- **Description:** DES usage
- **Evidence (Line):** `"Two-key TripleDES (16-byte keys) is deprecated and "`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 851. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/hazmat/decrepit/ciphers/algorithms.py:17
- **Description:** RC4 usage
- **Evidence (Line):** `class ARC4(CipherAlgorithm):`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 852. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/x509/extensions.py:72
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(data).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 853. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/cryptography/x509/extensions.py:72
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(data).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 854. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/dnssec.py:224
- **Description:** SHA1 usage
- **Evidence (Line):** `dshash = hashlib.sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 855. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/dnssec.py:746
- **Description:** SHA1 usage
- **Evidence (Line):** `digest = hashlib.sha1(domain_encoded + salt_encoded).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 856. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/dnssec.py:748
- **Description:** SHA1 usage
- **Evidence (Line):** `digest = hashlib.sha1(digest + salt_encoded).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 857. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/dnssec.py:224
- **Description:** Weak hash algorithm
- **Evidence (Line):** `dshash = hashlib.sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 858. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/dnssec.py:746
- **Description:** Weak hash algorithm
- **Evidence (Line):** `digest = hashlib.sha1(domain_encoded + salt_encoded).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 859. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/dnssec.py:748
- **Description:** Weak hash algorithm
- **Evidence (Line):** `digest = hashlib.sha1(digest + salt_encoded).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 860. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/entropy.py:37
- **Description:** SHA1 usage
- **Evidence (Line):** `self.hash = hashlib.sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 861. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/entropy.py:37
- **Description:** Weak hash algorithm
- **Evidence (Line):** `self.hash = hashlib.sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 862. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/tsig.py:167
- **Description:** Weak hash algorithm
- **Evidence (Line):** `HMAC_SHA1: hashlib.sha1,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 863. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/dns/tsig.py:175
- **Description:** Weak hash algorithm
- **Evidence (Line):** `HMAC_MD5: hashlib.md5,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 864. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/duckdb/experimental/spark/sql/functions.py:3423
- **Description:** MD5 usage
- **Evidence (Line):** `def md5(col: "ColumnOrName") -> Column:`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 865. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/duckdb/experimental/spark/sql/functions.py:3443
- **Description:** MD5 usage
- **Evidence (Line):** `>>> spark.createDataFrame([("ABC",)], ["a"]).select(md5("a").alias("hash")).collect()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 866. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/flask/sessions.py:276
- **Description:** SHA1 usage
- **Evidence (Line):** `def _lazy_sha1(string: bytes = b"") -> t.Any:`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 867. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/flask/sessions.py:281
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(string)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 868. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/flask/sessions.py:277
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"""Don't access ``hashlib.sha1`` until runtime. FIPS builds may not include`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 869. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/flask/sessions.py:281
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(string)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 870. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/tests/abstract/__init__.py:228
- **Description:** MD5 usage
- **Evidence (Line):** `hashed_i = md5(str(i).encode("utf-8")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 871. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/tests/abstract/copy.py:548
- **Description:** MD5 usage
- **Evidence (Line):** `hashed_i = md5(str(i).encode("utf-8")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 872. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/tests/abstract/get.py:576
- **Description:** MD5 usage
- **Evidence (Line):** `hashed_i = md5(str(i).encode("utf-8")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 873. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/tests/abstract/put.py:582
- **Description:** MD5 usage
- **Evidence (Line):** `hashed_i = md5(str(i).encode("utf-8")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 874. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/utils.py:321
- **Description:** MD5 usage
- **Evidence (Line):** `h = md5(str(args).encode())`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 875. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/fsspec/utils.py:324
- **Description:** MD5 usage
- **Evidence (Line):** `h = md5(str(args).encode(), usedforsecurity=False)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 876. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_auth.py:309
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(s).hexdigest()[:16].encode()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 877. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_auth.py:177
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"MD5": hashlib.md5,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 878. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_auth.py:178
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"MD5-SESS": hashlib.md5,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 879. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_auth.py:179
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"SHA": hashlib.sha1,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 880. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_auth.py:180
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"SHA-SESS": hashlib.sha1,`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 881. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx/_auth.py:309
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(s).hexdigest()[:16].encode()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 882. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx2/_auth.py:300
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(s).hexdigest()[:16].encode()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 883. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/httpx2/_auth.py:300
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(s).hexdigest()[:16].encode()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 884. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/itsdangerous/signer.py:40
- **Description:** SHA1 usage
- **Evidence (Line):** `def _lazy_sha1(string: bytes = b"") -> t.Any:`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 885. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/itsdangerous/signer.py:45
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(string)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 886. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/itsdangerous/signer.py:41
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"""Don't access ``hashlib.sha1`` until runtime. FIPS builds may not include`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 887. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/itsdangerous/signer.py:45
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(string)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 888. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/itsdangerous/signer.py:96
- **Description:** Weak hash algorithm
- **Evidence (Line):** `defaults to :func:`hashlib.sha1`. Note that the security of the`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 889. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/itsdangerous/signer.py:115
- **Description:** Weak hash algorithm
- **Evidence (Line):** `#: :func:`hashlib.sha1`, but can be changed to any :mod:`hashlib` or`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 890. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/bccache.py:156
- **Description:** SHA1 usage
- **Evidence (Line):** `hash = sha1(name.encode("utf-8"))`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 891. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/bccache.py:165
- **Description:** SHA1 usage
- **Evidence (Line):** `return sha1(source.encode("utf-8")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 892. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/jinja2/loaders.py:661
- **Description:** SHA1 usage
- **Evidence (Line):** `return "tmpl_" + sha1(name.encode("utf-8")).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 893. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:212
- **Description:** MD5 usage
- **Evidence (Line):** `In [23]: %timeit hashlib.md5(a).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 894. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:215
- **Description:** MD5 usage
- **Evidence (Line):** `In [24]: %timeit hashlib.md5(pickle.dumps(a, protocol=2)).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 895. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:218
- **Description:** MD5 usage
- **Evidence (Line):** `In [25]: %timeit hashlib.md5(cPickle.dumps(a, protocol=2)).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 896. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:228
- **Description:** MD5 usage
- **Evidence (Line):** `return hashlib.md5(memoryview(x)).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 897. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:212
- **Description:** Weak hash algorithm
- **Evidence (Line):** `In [23]: %timeit hashlib.md5(a).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 898. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:215
- **Description:** Weak hash algorithm
- **Evidence (Line):** `In [24]: %timeit hashlib.md5(pickle.dumps(a, protocol=2)).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 899. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:218
- **Description:** Weak hash algorithm
- **Evidence (Line):** `In [25]: %timeit hashlib.md5(cPickle.dumps(a, protocol=2)).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 900. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/joblib/test/test_hashing.py:228
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.md5(memoryview(x)).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 901. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:46
- **Description:** SHA1 usage
- **Evidence (Line):** `hash_value = hashlib.sha1(`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 902. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:55
- **Description:** SHA1 usage
- **Evidence (Line):** `def _warn_about_sha1() -> None:`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 903. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:78
- **Description:** SHA1 usage
- **Evidence (Line):** `_warn_about_sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 904. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:163
- **Description:** SHA1 usage
- **Evidence (Line):** `digest = hashlib.sha1(text.encode("utf-8"), usedforsecurity=False).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 905. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:409
- **Description:** SHA1 usage
- **Evidence (Line):** `_warn_about_sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 906. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:748
- **Description:** SHA1 usage
- **Evidence (Line):** `_warn_about_sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 907. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:46
- **Description:** Weak hash algorithm
- **Evidence (Line):** `hash_value = hashlib.sha1(`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 908. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langchain_core/indexing/api.py:163
- **Description:** Weak hash algorithm
- **Evidence (Line):** `digest = hashlib.sha1(text.encode("utf-8"), usedforsecurity=False).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 909. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/langgraph/pregel/_algo.py:1397
- **Description:** SHA1 usage
- **Evidence (Line):** `sha = sha1(namespace, usedforsecurity=False)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 910. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/llama_index/core/retrievers/fusion_retriever.py:24
- **Description:** DES usage
- **Evidence (Line):** `class FUSION_MODES(str, Enum):`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 911. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/msal/managed_identity.py:678
- **Description:** SHA1 usage
- **Evidence (Line):** `actual_thumbprint = hashlib.sha1(certificate).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 912. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/msal/managed_identity.py:678
- **Description:** Weak hash algorithm
- **Evidence (Line):** `actual_thumbprint = hashlib.sha1(certificate).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 913. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/downloader.py:2578
- **Description:** MD5 usage
- **Evidence (Line):** `md5_digest = md5()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 914. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader.py:130
- **Description:** MD5 usage
- **Evidence (Line):** `checksum = hashlib.md5(b"x").hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 915. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader.py:163
- **Description:** MD5 usage
- **Evidence (Line):** `return_value=hashlib.md5(b"x").hexdigest(),`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 916. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader.py:130
- **Description:** Weak hash algorithm
- **Evidence (Line):** `checksum = hashlib.md5(b"x").hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 917. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader.py:163
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return_value=hashlib.md5(b"x").hexdigest(),`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 918. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader_atomic.py:35
- **Description:** MD5 usage
- **Evidence (Line):** `"md5": hashlib.md5(data).hexdigest(),`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 919. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader_atomic.py:98
- **Description:** MD5 usage
- **Evidence (Line):** `data["zip_md5"] = hashlib.md5(content).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 920. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader_atomic.py:272
- **Description:** MD5 usage
- **Evidence (Line):** `checksum=hashlib.md5(zb).hexdigest(),`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 921. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader_atomic.py:35
- **Description:** Weak hash algorithm
- **Evidence (Line):** `"md5": hashlib.md5(data).hexdigest(),`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 922. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader_atomic.py:98
- **Description:** Weak hash algorithm
- **Evidence (Line):** `data["zip_md5"] = hashlib.md5(content).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 923. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/nltk/test/unit/test_downloader_atomic.py:272
- **Description:** Weak hash algorithm
- **Evidence (Line):** `checksum=hashlib.md5(zb).hexdigest(),`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 924. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/requests/auth.py:179
- **Description:** MD5 usage
- **Evidence (Line):** `return hashlib.md5(x, usedforsecurity=False).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 925. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/requests/auth.py:187
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(x, usedforsecurity=False).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 926. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/requests/auth.py:237
- **Description:** SHA1 usage
- **Evidence (Line):** `cnonce = hashlib.sha1(s, usedforsecurity=False).hexdigest()[:16]`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 927. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/requests/auth.py:179
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.md5(x, usedforsecurity=False).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 928. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/requests/auth.py:187
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(x, usedforsecurity=False).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 929. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/requests/auth.py:237
- **Description:** Weak hash algorithm
- **Evidence (Line):** `cnonce = hashlib.sha1(s, usedforsecurity=False).hexdigest()[:16]`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 930. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/rich/tree.py:18
- **Description:** DES usage
- **Evidence (Line):** `ASCII_GUIDES (GuideType): Guide lines used when Console.ascii_only is True.`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 931. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/rich/tree.py:19
- **Description:** DES usage
- **Evidence (Line):** `TREE_GUIDES (List[GuideType, GuideType, GuideType]): Default guide lines.`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 932. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/dialects/mysql/base.py:497
- **Description:** MD5 usage
- **Evidence (Line):** `table.select(table.c.password == func.md5("plaintext"))`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 933. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/testing/plugin/pytestplugin.py:561
- **Description:** MD5 usage
- **Evidence (Line):** `digest = hashlib.md5(`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 934. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/testing/plugin/pytestplugin.py:561
- **Description:** Weak hash algorithm
- **Evidence (Line):** `digest = hashlib.md5(`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 935. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/compat.py:138
- **Description:** MD5 usage
- **Evidence (Line):** `return hashlib.md5(usedforsecurity=False)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 936. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/sqlalchemy/util/compat.py:138
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.md5(usedforsecurity=False)`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 937. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/starlette/responses.py:340
- **Description:** MD5 usage
- **Evidence (Line):** `etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 938. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/starlette/responses.py:340
- **Description:** Weak hash algorithm
- **Evidence (Line):** `etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 939. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/tiktoken/load.py:51
- **Description:** SHA1 usage
- **Evidence (Line):** `cache_key = hashlib.sha1(blobpath.encode()).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 940. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/tiktoken/load.py:51
- **Description:** Weak hash algorithm
- **Evidence (Line):** `cache_key = hashlib.sha1(blobpath.encode()).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 941. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/websockets/utils.py:34
- **Description:** SHA1 usage
- **Evidence (Line):** `sha1 = hashlib.sha1((key + GUID).encode()).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 942. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/websockets/utils.py:34
- **Description:** Weak hash algorithm
- **Evidence (Line):** `sha1 = hashlib.sha1((key + GUID).encode()).digest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 943. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:45
- **Description:** SHA1 usage
- **Evidence (Line):** `return hashlib.sha1(f"{pin} added salt".encode("utf-8", "replace")).hexdigest()[:12]`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 944. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:196
- **Description:** SHA1 usage
- **Evidence (Line):** `h = hashlib.sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 945. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:45
- **Description:** Weak hash algorithm
- **Evidence (Line):** `return hashlib.sha1(f"{pin} added salt".encode("utf-8", "replace")).hexdigest()[:12]`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 946. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/debug/__init__.py:196
- **Description:** Weak hash algorithm
- **Evidence (Line):** `h = hashlib.sha1()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High

### 947. [Medium] Weak Cryptography
- **File:** .venv-test/lib/python3.12/site-packages/werkzeug/http.py:981
- **Description:** SHA1 usage
- **Evidence (Line):** `return sha1(data).hexdigest()`
- **Exploit Scenario:** Weak algorithms vulnerable to collision/brute force attacks
- **Fix Recommendation:** Use modern algorithms (SHA-256+, bcrypt/argon2 for passwords, secrets module for tokens)
- **Confidence:** High
