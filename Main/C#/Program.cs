using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;

internal static class Program
{
    // --------- CONFIG DEFAULTS (you can change at runtime) ----------
    private const int DefaultRsaBits = 2048;
    private const int DefaultValidityDays = 3650;   // 10 years (X.509 always has an expiry)
    private const string DefaultSubjectCN = "CN=Salesforce JWT Cert";
    private const string DefaultOutputDir = "sf-jwt-out";

    public static async Task Main()
    {
        Console.WriteLine("Salesforce JWT Tool");
        Console.WriteLine("--------------------");
        Console.WriteLine("1) Generate RSA key pair + self-signed X.509 certificate");
        Console.WriteLine("2) Create signed JWT (RS256)");
        Console.WriteLine("3) (Optional) Exchange JWT for access token");
        Console.WriteLine("Choose an option (1-3): ");
        var choice = Console.ReadLine();

        switch (choice)
        {
            case "1":
                GenerateKeysAndCert();
                break;
            case "2":
                CreateSignedJwt();
                break;
            case "3":
                await ExchangeJwtForAccessTokenAsync();
                break;
            default:
                Console.WriteLine("Goodbye.");
                break;
        }
    }

    private static void GenerateKeysAndCert()
    {
        Console.Write($"Output directory [{DefaultOutputDir}]: ");
        var outDir = ReadOrDefault(DefaultOutputDir);
        Directory.CreateDirectory(outDir);

        Console.Write($"RSA key size [{DefaultRsaBits}]: ");
        var bits = int.TryParse(Console.ReadLine(), out var b) ? b : DefaultRsaBits;

        Console.Write($"Certificate subject (DN) [{DefaultSubjectCN}]: ");
        var subject = ReadOrDefault(DefaultSubjectCN);

        Console.Write($"Validity (days) [{DefaultValidityDays}]: ");
        var days = int.TryParse(Console.ReadLine(), out var d) ? d : DefaultValidityDays;

        Console.Write("Create a password-protected PFX? (y/N): ");
        var mkPfx = Console.ReadLine()?.Trim().Equals("y", StringComparison.OrdinalIgnoreCase) == true;

        string pfxPassword = "";
        if (mkPfx)
        {
            Console.Write("PFX password: ");
            pfxPassword = ReadPassword();
        }

        var now = DateTimeOffset.UtcNow;
        using var rsa = RSA.Create(bits);

        // Build self-signed cert (SHA256 with RSA, PKCS#1 padding)
        var req = new CertificateRequest(subject, rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        // Add basic extensions (optional)
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(
            X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, false));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));

        using var cert = req.CreateSelfSigned(now.AddDays(-1), now.AddDays(days)); // notBefore yesterday to avoid clock skew

        // Export certificate (PEM)
        var certDer = cert.Export(X509ContentType.Cert);
        var certPem = PemEncode("CERTIFICATE", certDer);

        // Export private key (PKCS#8 PEM)
        var pkcs8 = rsa.ExportPkcs8PrivateKey();
        var keyPem = PemEncode("PRIVATE KEY", pkcs8);

        var baseName = Path.Combine(outDir, "salesforce-jwt");
        var certPath = baseName + ".crt";
        var keyPath = baseName + ".key";
        File.WriteAllText(certPath, certPem);
        File.WriteAllText(keyPath, keyPem);

        Console.WriteLine();
        Console.WriteLine("Files created:");
        Console.WriteLine($"  Public certificate (upload to Salesforce Connected App): {certPath}");
        Console.WriteLine($"  Private key (KEEP SECRET):                               {keyPath}");

        if (mkPfx)
        {
            using var certWithKey = cert.CopyWithPrivateKey(rsa);
            var pfxBytes = certWithKey.Export(X509ContentType.Pfx, pfxPassword);
            var pfxPath = baseName + ".pfx";
            File.WriteAllBytes(pfxPath, pfxBytes);
            Console.WriteLine($"  PFX (for Windows/ .NET use):                             {pfxPath}");
        }

        Console.WriteLine("\nNext steps:");
        Console.WriteLine("- In Salesforce Setup → App Manager → your Connected App → Edit → Upload Certificate (use the .crt).");
        Console.WriteLine("- Copy the Consumer Key from the Connected App; you’ll need it for JWT `iss`.");
        Console.WriteLine("That's it! Hit enter to exit the program");
        Console.ReadLine();

        // (Certificate creation via .NET’s CertificateRequest and export to PEM/PFX is supported in modern .NET) 
        // (Refs: Microsoft docs on CertificateRequest; exporting with CopyWithPrivateKey/PFX.) 
        // Doc refs are in the written guide.
    }

    //private static void CreateSignedJwt()
    //{
    //    Console.Write("Path to private key (.key PKCS#8 PEM) OR .pfx");
    //    Console.Write("\n I.e.: 'C:\\Users\\YourUser\\Downloads\\SfJwtTool\\sf-jwt-out\\salesforce-jwt.key':");
    //    //var keyPath = ReadOrDefault(DefaultOutputDir);
    //    var keyPath = Console.ReadLine()?.Trim() ?? "";

    //    bool isPfx = keyPath.EndsWith(".pfx", StringComparison.OrdinalIgnoreCase);
    //    RSA rsa;

    //    if (isPfx)
    //    {
    //        //Console.Write("PFX password: ");
    //        //var pwd = ReadPassword();
    //        //var cert = new X509Certificate2(keyPath, pwd,
    //        //    X509KeyStorageFlags.MachineKeySet | X509KeyStorageFlags.Exportable);
    //        //rsa = cert.GetRSAPrivateKey() ?? throw new InvalidOperationException("PFX has no RSA private key.");
    //        Console.Write("PFX password: ");
    //        var pwd = ReadPassword();
    //        var cert = new X509Certificate2(keyPath, pwd,
    //             X509KeyStorageFlags.MachineKeySet | X509KeyStorageFlags.Exportable);
    //        rsa = cert.GetRSAPrivateKey() ?? throw new InvalidOperationException("PFX has no RSA private key.");

    //    }
    //    else
    //    {
    //        // Load PKCS#8 PEM PRIVATE KEY
    //        var pem = File.ReadAllText(keyPath);
    //        rsa = RSA.Create();
    //        rsa.ImportFromPem(pem);
    //    }

    //    Console.Write("Consumer Key (Connected App) [iss]: ");
    //    var consumerKey = Console.ReadLine()?.Trim() ?? "";

    //    Console.Write("Salesforce Username [sub]: ");
    //    var username = Console.ReadLine()?.Trim() ?? "";

    //    Console.Write("Audience [aud] (login.salesforce.com or test.salesforce.com): ");
    //    var audHost = Console.ReadLine()?.Trim();
    //    if (string.IsNullOrWhiteSpace(audHost)) audHost = "https://login.salesforce.com";

    //    Console.Write("Expiration minutes (typ. 3-5) [3]: ");
    //    var mins = int.TryParse(Console.ReadLine(), out var m) ? m : 3;

    //    // Build & sign JWT (RS256)
    //    var creds = new SigningCredentials(new RsaSecurityKey(rsa), SecurityAlgorithms.RsaSha256);
    //    var now = DateTimeOffset.UtcNow;
    //    var handler = new JwtSecurityTokenHandler();
    //    var jwt = new JwtSecurityToken(
    //        issuer: null,
    //        audience: audHost,
    //        claims: null,
    //        notBefore: now.UtcDateTime,
    //        expires: now.AddMinutes(mins).UtcDateTime,
    //        signingCredentials: creds
    //    );
    //    jwt.Payload["iss"] = consumerKey; // Salesforce requires iss=sub=aud as defined in docs
    //    jwt.Payload["sub"] = username;

    //    var token = handler.WriteToken(jwt);
    //    Console.WriteLine("\n===== SIGNED JWT (assertion) =====\n");
    //    Console.WriteLine(token);
    //    Console.WriteLine("\n(Use this in the token request: grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer & assertion=<above>)");

    //    rsa.Dispose();

    //    Console.WriteLine("\nReminder: POST to /services/oauth2/token at the correct host (login or test) for JWT bearer flow.");
    //    // As per Salesforce docs: RS256-signed JWT, grant_type for JWT-bearer, no client_secret, no refresh token. 
    //}


    private static void CreateSignedJwt()
    {
        RSA rsa = null;
        string keyPath = "";
        bool isPfx = false;

        // Retry loop for loading the private key
        while (rsa == null)
        {
            try
            {
                //Console.Write("Path to private key (.key PKCS#8 PEM) OR .pfx");
                //Console.Write("\nI.e.: 'C:\\Users\\YourUser\\Downloads\\SfJwtTool\\sf-jwt-out\\salesforce-jwt.key': ");
                //keyPath = Console.ReadLine()?.Trim() ?? "";

                //isPfx = keyPath.EndsWith(".pfx", StringComparison.OrdinalIgnoreCase);


                Console.Write("Path to private key (.key PKCS#8 PEM) OR .pfx");
                Console.Write("\nI.e.: 'C:\\Users\\YourUser\\Downloads\\SfJwtTool\\sf-jwt-out\\salesforce-jwt.key': ");
                keyPath = Console.ReadLine()?.Trim() ?? "";

                if (string.IsNullOrWhiteSpace(keyPath))
                {
                    Console.WriteLine("No path entered. Please try again.\n");
                    continue;
                }

                if (!File.Exists(keyPath))
                {
                    Console.WriteLine("File not found. Please check the path and try again.\n");
                    continue;
                }
                isPfx = keyPath.EndsWith(".pfx", StringComparison.OrdinalIgnoreCase);

                if (isPfx)
                {
                    Console.Write("PFX password: ");
                    var pwd = ReadPassword();
                    var cert = new X509Certificate2(keyPath, pwd,
                        X509KeyStorageFlags.MachineKeySet | X509KeyStorageFlags.Exportable);
                    rsa = cert.GetRSAPrivateKey() ?? throw new InvalidOperationException("PFX has no RSA private key.");
                }
                else
                {
                    var pem = File.ReadAllText(keyPath);
                    rsa = RSA.Create();
                    rsa.ImportFromPem(pem);
                }
            }
            catch (Exception ex) when (
                ex is FileNotFoundException ||
                ex is UnauthorizedAccessException ||
                ex is CryptographicException ||
                ex is InvalidOperationException ||
                ex is IOException)
            {
                Console.WriteLine($"\nError: {ex.Message}");
                Console.WriteLine("Please check the path and try again.\n");
            }
        }

        try
        {
            Console.Write("Consumer Key (Connected App) [iss]: ");
            var consumerKey = Console.ReadLine()?.Trim() ?? "";

            Console.Write("Salesforce Username [sub]: ");
            var username = Console.ReadLine()?.Trim() ?? "";

            //Console.Write("Audience [aud] (login.salesforce.com or test.salesforce.com): ");
            //var audHost = Console.ReadLine()?.Trim();
            //if (string.IsNullOrWhiteSpace(audHost)) audHost = "https://login.salesforce.com";


            Console.Write("Select audience (1 = Production (login), 2 = Sandbox (test)): ");
            var audChoice = Console.ReadLine()?.Trim();

            string audHost = audChoice switch
            {
                "1" => "https://login.salesforce.com",
                "2" => "https://test.salesforce.com",
                _ => "https://login.salesforce.com" // Default to Production if input is invalid or empty
            };

            Console.WriteLine($"Selected audience: {audHost}");


            Console.Write("Expiration minutes (typ. 3-5) [Default 3]: ");
            var mins = int.TryParse(Console.ReadLine(), out var m) ? m : 3;

            var creds = new SigningCredentials(new RsaSecurityKey(rsa), SecurityAlgorithms.RsaSha256);
            var now = DateTimeOffset.UtcNow;
            var handler = new JwtSecurityTokenHandler();
            var jwt = new JwtSecurityToken(
                issuer: null,
                audience: audHost,
                claims: null,
                notBefore: now.UtcDateTime,
                expires: now.AddMinutes(mins).UtcDateTime,
                signingCredentials: creds
            );
            jwt.Payload["iss"] = consumerKey;
            jwt.Payload["sub"] = username;

            var token = handler.WriteToken(jwt);
            Console.WriteLine("\n===== SIGNED JWT (assertion) =====\n");
            Console.WriteLine(token);
            Console.WriteLine("\n(Use this in the token request: grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer & assertion=<above>)");
            Console.ReadLine();
            Console.WriteLine("Make sure to copy your JWT token and hit enter to exit.");
            Console.ReadLine();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\nUnexpected error while creating JWT: {ex.Message}");
        }
        finally
        {
            rsa?.Dispose();
            Console.WriteLine("\nReminder: POST to /services/oauth2/token at the correct host (login or test) for JWT bearer flow.");
        }
    }


    private static async Task ExchangeJwtForAccessTokenAsync()
    {
        //Console.Write("OAuth token URL (prod: https://login.salesforce.com/services/oauth2/token, sandbox: https://test.salesforce.com/services/oauth2/token): ");
        //var tokenUrl = Console.ReadLine()?.Trim() ?? "";


        Console.Write("Select environment (1 = Production (login), 2 = Sandbox (test)): ");
        var envChoice = Console.ReadLine()?.Trim();

        string tokenUrl = envChoice switch
        {
            "1" => "https://login.salesforce.com/services/oauth2/token",
            "2" => "https://test.salesforce.com/services/oauth2/token",
            _ => ""
        };

        if (string.IsNullOrEmpty(tokenUrl))
        {
            Console.WriteLine("Invalid selection. Please enter 1 or 2.");
            // Optionally, you could loop until a valid input is received
        }
        else
        {
            Console.WriteLine($"Selected token URL: {tokenUrl}");
        }

        Console.Write("Paste the signed JWT (assertion): ");
        var assertion = Console.ReadLine()?.Trim() ?? "";

        using var http = new HttpClient();
        var form = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("grant_type", "urn:ietf:params:oauth:grant-type:jwt-bearer"),
            new KeyValuePair<string, string>("assertion", assertion),
        });

        //Console.WriteLine("\nRequesting access token...");
        //var resp = await http.PostAsync(tokenUrl, form);
        //var body = await resp.Content.ReadAsStringAsync();
        //if (!resp.IsSuccessStatusCode)
        //{
        //    Console.WriteLine($"FAILED: {resp.StatusCode}\n{body}");
        //    Console.ReadLine();
        //    return;
        //    Console.ReadLine();
        //}
        //Console.WriteLine("SUCCESS:");
        //Console.WriteLine(body);
        //Console.WriteLine("\nUse the access_token with: Authorization: Bearer <token>");

        Console.WriteLine("\nRequesting access token...");

        try
        {
            var resp = await http.PostAsync(tokenUrl, form);
            var body = await resp.Content.ReadAsStringAsync();

            if (!resp.IsSuccessStatusCode)
            {
                Console.WriteLine($"\nFAILED: {resp.StatusCode}");
                Console.WriteLine($"Response body:\n{body}");
                Console.WriteLine("Please verify the token URL and JWT assertion, then try again.");
                Console.WriteLine("Press Enter to exit...");
                Console.ReadLine();
                return;
            }

            Console.WriteLine("\nSUCCESS:");
            Console.WriteLine(body);
            Console.WriteLine("\nUse the access_token with: Authorization: Bearer <token>");
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"\nNetwork error: {ex.Message}");
            Console.WriteLine("Please check your internet connection and try again.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\nUnexpected error: {ex.Message}");
            Console.WriteLine("Please review your inputs and try again.");
        }

        Console.WriteLine("\nPress Enter to continue...");
        Console.ReadLine();

    }



    private static string ReadOrDefault(string def)
    {
        var s = Console.ReadLine();
        return string.IsNullOrWhiteSpace(s) ? def : s.Trim();
    }

    private static string ReadPassword()
    {
        var sb = new StringBuilder();
        ConsoleKeyInfo key;
        while ((key = Console.ReadKey(true)).Key != ConsoleKey.Enter)
        {
            if (key.Key == ConsoleKey.Backspace && sb.Length > 0)
            {
                sb.Length--;
                continue;
            }
            if (!char.IsControl(key.KeyChar)) sb.Append(key.KeyChar);
        }
        Console.WriteLine();
        return sb.ToString();
    }

    private static string PemEncode(string label, byte[] der)
    {
        var b64 = Convert.ToBase64String(der);
        var sb = new StringBuilder();
        sb.AppendLine($"-----BEGIN {label}-----");
        for (int i = 0; i < b64.Length; i += 64)
            sb.AppendLine(b64.Substring(i, Math.Min(64, b64.Length - i)));
        sb.AppendLine($"-----END {label}-----");
        return sb.ToString();
    }
}