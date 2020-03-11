﻿using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rl.Net.Cli
{
    static internal class Helpers
    {
        public static void WriteErrorAndExit(string errorMessage, int exitCode = -1)
        {
            Console.Error.WriteLine(errorMessage);
            Environment.Exit(exitCode);
        }

        public static void WriteStatusAndExit(ApiStatus apiStatus)
        {
            WriteErrorAndExit(apiStatus.ErrorMessage);
        }

        public static void WriteStatusAndExit(RLException exception)
        {
            WriteErrorAndExit(exception.Message);
        }

        public static LiveModel CreateLiveModelOrExit(string clientJsonPath)
        {
            if (!File.Exists(clientJsonPath))
            {
                WriteErrorAndExit($"Could not find file with path '{clientJsonPath}'.");
            }

            string json = File.ReadAllText(clientJsonPath);

            ApiStatus apiStatus = new ApiStatus();

            Configuration config;
            if (!Configuration.TryLoadConfigurationFromJson(json, out config, apiStatus))
            {
                WriteStatusAndExit(apiStatus);
            }

            LiveModel liveModel = new LiveModel(config);

            liveModel.BackgroundError += LiveModel_BackgroundError;
            liveModel.TraceLoggerEvent += LiveModel_TraceLogEvent;

            if (!liveModel.TryInit(apiStatus))
            {
                WriteStatusAndExit(apiStatus);
            }

            return liveModel;
        }

        public static RlLogger CreateRlLoggerOrExit(string clientJsonPath)
        {
            if (!File.Exists(clientJsonPath))
            {
                WriteErrorAndExit($"Could not find file with path '{clientJsonPath}'.");
            }

            string json = File.ReadAllText(clientJsonPath);

            ApiStatus apiStatus = new ApiStatus();

            Configuration config;
            if (!Configuration.TryLoadConfigurationFromJson(json, out config, apiStatus))
            {
                WriteStatusAndExit(apiStatus);
            }

            var logger = new RlLogger(config);

            logger.BackgroundError += LiveModel_BackgroundError;
            logger.TraceLoggerEvent += LiveModel_TraceLogEvent;

            try
            {
                logger.Init();
            }
            catch (RLException e)
            {
                WriteStatusAndExit(e);
            }

            return logger;
        }

        public static void LiveModel_BackgroundError(object sender, ApiStatus e)
        {
            Console.Error.WriteLine(e.ErrorMessage);
        }

        public static void LiveModel_TraceLogEvent(object sender, TraceLogEventArgs e)
        {
            RLLogLevel logLevel = e.LogLevel;
            switch (logLevel)
            {
                case RLLogLevel.LEVEL_ERROR:
                    Console.Error.WriteLine($"LogLevel: {e.LogLevel} LogMessage: {e.Message}");
                    break;
                default:
                    Console.WriteLine($"LogLevel: {e.LogLevel} LogMessage: {e.Message}");
                    break;
            }
        }
    }
}
